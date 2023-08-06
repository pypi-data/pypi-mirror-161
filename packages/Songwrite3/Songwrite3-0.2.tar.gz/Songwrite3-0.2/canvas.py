# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2007-2016 Jean-Baptiste LAMY -- jibalamy@free.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later verson.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, os.path, sys, math, bisect, locale, codecs
from io import StringIO

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui

from editobj3.introsp  import *
from editobj3.observe  import *
from editobj3.undoredo import *
import editobj3.editor_qt as editor_qt

import songwrite3.globdef as globdef
import songwrite3.model   as model
import songwrite3.stemml  as stemml
import songwrite3.player  as player
import songwrite3.__editobj3__

zoom_levels          = [0.25, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
ZOOM_2_CLIP_DURATION = {
  0.25 : 96,
  0.35 : 96,
  0.5  : 96,
  0.75 : 48,
  1.0  : 48,
  1.5  : 24,
  2.0  : 24,
  3.0  : 12,
  4.0  : 12,
  }


SELECTION_COLOR  = None
SELECTION_COLOR2 = None

CLIPBOARD        = None
CLIPBOARD_SOURCE = None
CLIPBOARD_X1     = 0
CLIPBOARD_Y1     = 0
CLIPBOARD_X2     = 0
CLIPBOARD_Y2     = 0

CLIPBOARD2_NAME = "_SONGWRITE3_NOTES"
#CLIPBOARD2 = gtk.Clipboard(selection = CLIPBOARD2_NAME)

SONGWRITE_MIME_TYPE = "application/sw-xml"

WHITE_STEM_COLOR = qtgui.QColor(204, 204, 204)

BIG_PEN = qtgui.QPen(qtcore.Qt.black)
BIG_PEN.setWidth(2)

def find_view_children(o):
  if isinstance(o, model.View) and hasattr(o, "strings"):
    return o.strings
  return []

class SongwriteMimeData(qtcore.QMimeData):
  def __init__(self, canvas, notes, x, y):
    qtcore.QMimeData.__init__(self)
    self.canvas = canvas
    self.notes  = notes
    self.xml    = None
    self.x      = x
    self.y      = y
    
  def formats(self): return [SONGWRITE_MIME_TYPE]
  
  def generate_xml(self): self.xml = self.canvas.on_drag_data_get(self.notes, self.x, self.y)
  
  def data(self, mimetype = SONGWRITE_MIME_TYPE):
    if not self.xml: self.generate_xml()
    return qtcore.QByteArray(self.xml.encode("utf8"))


class FixedLayout(qtwidgets.QLayout):
  def __init__(self):
    qtwidgets.QLayout.__init__(self)
    self._items = []
    self._widget_2_item = {}
    self._widget_2_rect = {}
    
  def addItem(self, item):
    self._items.append(item)
    self._widget_2_item[item.widget()] = item
    self._widget_2_rect[item.widget()] = 0, 0, 100, 100
  def count(self): return len(self._items)
  def itemAt(self, i):
    if 0 <= i < len(self._items): return self._items[i]
  def takeAt(self, i):
    if 0 <= i < len(self._items):
      item = self._items[i]
      del self._items[i]
      return item
    return 0
  
  def setGeometry(self, rect):
    for item in self._items:
      item.widget().setGeometry(qtcore.QRect(*self._widget_2_rect[item.widget()]))
      
  def sizeHint(self): return qtcore.QSize()
  def minimumSize(self): return qtcore.QSize()
  
  def move_widget(self, widget, x, y):
    if (x, y) != self._widget_2_rect[widget][:2]:
      self._widget_2_rect[widget] = int(x), int(y), int(self._widget_2_rect[widget][2]), int(self._widget_2_rect[widget][3])
      self._widget_2_item[widget].widget().setGeometry(qtcore.QRect(*self._widget_2_rect[widget]))
      
  def resize_widget(self, widget, width, height):
    if (width, height) != self._widget_2_rect[widget][2:]:
      self._widget_2_rect[widget] = int(self._widget_2_rect[widget][0]), int(self._widget_2_rect[widget][1]), int(width), int(height)
      self._widget_2_item[widget].widget().setGeometry(qtcore.QRect(*self._widget_2_rect[widget]))
      
  def move_resize_widget(self, widget, x, y, width, height):
    if (x, y, width, height) != self._widget_2_rect[widget]:
      self._widget_2_rect[widget] = int(x), int(y), int(width), int(height)
      #self._widget_2_item[widget].setGeometry(qtcore.QRect(*self._widget_2_rect[widget]))
      self._widget_2_item[widget].widget().setGeometry(qtcore.QRect(*self._widget_2_rect[widget]))
      
class BaseCanvas(object):
  def __init__(self, song, zoom = 1.0):
    self.x                   = 0
    self.y                   = 0
    self.width               = 0
    self.height              = 0
    self.song                = song
    self.zoom                = zoom
    self.selection_x1        = 1000000
    self.selection_y1        = 1000000
    self.selection_x2        = -1
    self.selection_y2        = -1
    self.cursor              = None
    self.cursor_drawer       = None
    self.drawers             = None
    self.partition_2_drawer  = {}
    self.selections          = set()
    self.set_default_font_size(16.0)
    
  def set_default_font_size(self, size, device = None):
    self.default_font_size   = size
    #self.scale               = self.default_font_size / 14.6666666667
    #self.scale               = self.default_font_size / 11.0
    self.default_line_height = 0
    
    def mkfont(family, size, extra = -1):
      font = qtgui.QFont(family, int(size + 0.5), extra)
      if device:
        font = qtgui.QFont(font, device)
        font.setPixelSize(int(size))
      return font
    
    self.default_font      = mkfont("Sans" , self.default_font_size)
    self.title_font        = mkfont("Sans" , self.default_font_size * 1.2, qtgui.QFont.Bold)
    self.small_font        = mkfont("Sans" , self.default_font_size * 0.7)
    self.rhythm_font       = mkfont("Serif", self.default_font_size * 2.2, qtgui.QFont.Bold)
    self.rhythm_small_font = mkfont("Serif", self.default_font_size * 1.5, qtgui.QFont.Bold)
    
    self.default_metrics     = qtgui.QFontMetrics(self.default_font)
    self.default_ascent      = self.default_metrics.ascent()
    self.default_descent     = self.default_metrics.descent()
    self.default_line_height = self.default_metrics.height()
    self.char_h_size         = self.default_line_height // 2 # XXX
    
    self.scale    = 0.056818181818181816 * self.default_line_height
    self.start_x  = int((editor_qt.SMALL_ICON_SIZE + 42) * self.scale)
    
    self.small_metrics     = qtgui.QFontMetrics(self.small_font)
    self.small_ascent      = self.small_metrics.ascent()
    
    self.quarter_paths = { -1 : qtgui.QPainterPath(), 1 : qtgui.QPainterPath() }
    for sens in [-1, 1]:
      self.quarter_paths[sens].moveTo (0, 0)
      self.quarter_paths[sens].cubicTo(0               ,  3.0 * sens * self.scale,
                                       8.0 * self.scale,  3.0 * sens * self.scale,
                                       5.0 * self.scale, 12.0 * sens * self.scale)
      self.quarter_paths[sens].cubicTo(7.0 * self.scale,  9.0 * sens * self.scale,
                                       5.0 * self.scale,  6.0 * sens * self.scale,
                                       0.0             ,  3.0 * sens * self.scale)
    
    
  def reset(self):
    for drawer in self.drawers: drawer.destroy()
    self.drawers = []
    self.update_mesure_size()
    
  def text_extents_default(self, text):
    self.default_layout.set_text(text)
    return self.default_layout.get_pixel_size()
  
#  def draw_text_at_size(self, ctx, text, x, y, font_size_factor):
#    self.default_layout.set_font_description(pango.FontDescription(u"Sans %s" % (self.default_font_size * self.scale_pango_2_cairo * font_size_factor)))
#    ctx.move_to(x, y)
#    self.default_layout.set_text(text)
#    ctx.show_layout(self.default_layout)
#    self.default_layout.set_font_description(self.default_pango_font)
    
#  def draw_text_max_width(self, ctx, text, x, y, max_width):
#    ctx.move_to(x, y)
#    self.default_layout.set_text(text)
#    width0, height0 = self.default_layout.get_pixel_size()
#    if width0 < max_width:
#      ctx.show_layout(self.default_layout)
#    else:
#      font_size = self.default_font_size * self.scale_pango_2_cairo
#      while font_size:
#        font_size -= 1
#        self.default_layout.set_font_description(pango.FontDescription(u"Sans %s" % font_size))
#        width, height = self.default_layout.get_pixel_size()
#        if width < max_width: break
#      ctx.rel_move_to(0.0, 0.7 * (height0 - height))
#      ctx.show_layout(self.default_layout)
#      self.default_layout.set_font_description(self.default_pango_font)

  def note_string_id(self, note):
    return self.partition_2_drawer[note.partition].note_string_id(note)
  
  def y_2_drawer(self, y):
    for drawer in self.drawers:
      if y < drawer.y + drawer.height: return drawer
    return None
    
  def x_2_time(self, x):
    x0 = x - self.start_x + self.x
    if x0 <= 0: return 0.0
    mesure = self.song.mesure_at(x0 / self.zoom)
    if mesure is None:
      mesure = self.song.mesures[-1]
      if not mesure in self.mesure_2_extra_x: self.update_mesure_size()
      mesure_extra_x = self.mesure_2_extra_x[mesure]
      return (x0 - mesure_extra_x)  / self.zoom

    while 1:
      if not mesure in self.mesure_2_extra_x: self.update_mesure_size()
      mesure_extra_x = self.mesure_2_extra_x[mesure]
      time = (x0 - mesure_extra_x) / self.zoom
      mesure2 = self.song.mesure_at(time)
      if mesure2.time >= mesure.time:
        if time > mesure.end_time(): return mesure.end_time()
        return time
      mesure = mesure2
      
  def time_2_x(self, time):
    mesure = self.song.mesure_at(time)
    if not mesure in self.mesure_2_extra_x: self.update_mesure_size()
    return self.start_x - self.x + self.mesure_2_extra_x[mesure] + time * self.zoom
  
  #def time_2_x_barleft(self, time):
  #  mesure = self.song.mesure_at(time)
  #  return self.start_x - self.x + time * self.zoom
  
  def update_mesure_size(self):
    self.mesure_2_extra_x = {}
    extra_x = self.scale * 3.0
    for mesure in self.song.mesures + [None]:
      symbols = self.song.playlist.symbols.get(mesure)
      if symbols:
        for symbol in symbols:
          if   symbol.startswith(r"\repeat"):    extra_x += self.scale * 15.0
          elif symbol == r"} % end alternative": extra_x += self.scale * 15.0
          elif symbol == r"} % end repeat":      extra_x += self.scale * 15.0
      self.mesure_2_extra_x[mesure] = extra_x
      extra_x += self.scale * 5.0
    self.need_update_selection = 1
    
    
class Canvas(BaseCanvas, qtwidgets.QAbstractScrollArea):
  is_gui_interface = 1
  def __init__(self, main, song, zoom = 1.0):
    BaseCanvas.__init__(self, song, zoom)
    qtwidgets.QAbstractScrollArea.__init__(self)
    
    global SELECTION_COLOR
    if SELECTION_COLOR is None:
      global SELECTION_COLOR2
      import songwrite3.main
      color = songwrite3.main.app.palette().color(qtgui.QPalette.Highlight)
      SELECTION_COLOR  = qtgui.QColor(*[int(255 - 0.15 * (255 - c)) for c in [color.red(), color.green(), color.blue()]])
      SELECTION_COLOR2 = color
      
    self.main              = main
    self.song              = song
    self.last_selections   = set()
    self.click_x           = 0
    self.click_y           = 0
    self.last_selection_x1 = 1000000
    self.last_selection_y1 = 1000000
    self.last_selection_x2 = -1
    self.last_selection_y2 = -1
    self.need_update_selection = 0
    self.current_duration  = 48
    self.current_button    = 0
    self.previous_text     = "" # Previously typed text
    self.first_time        = 1
    self.x_before_tracking = -1
    self.touchscreen_new_note = None
    
    self.edit_timer = qtcore.QTimer()
    self.edit_timer.setSingleShot(True)
    self.edit_timer.timeout.connect(self.edit)
    self._note_to_edit = None
    
    self.set_default_font_size(globdef.config.FONTSIZE or qtgui.QFont().pointSize())
    
    self.horizontalScrollBar().setSingleStep(int(20 * self.scale))
    self.verticalScrollBar()  .setSingleStep(int(20 * self.scale))
    self.setAcceptDrops(True)
    self.viewport().setLayout(FixedLayout())
    
    observe(song                        , self.song_listener)
    observe(song.playlist               , self.playlist_listener)
    observe(song.playlist.playlist_items, self.playlist_listener)
    for item in song.playlist.playlist_items: observe(item, self.playlist_listener)
    observe(song.mesures                , self.mesures_listener)
    for mesure in song.mesures: observe(mesure, self.mesure_listener)
    
    observe(song.partitions, self.partitions_listener)
    for partition in song.partitions:
      observe(partition, self.partition_listener)
      if isinstance(partition, model.Partition):
        observe_tree(partition.view , self.view_listener, find_view_children)
        observe(partition.notes, self.notes_listener)
        for note in partition.notes: observe(note, self.note_listener)
        
    self.context_menu_song = qtwidgets.QMenu()
    menu_item = qtwidgets.QAction(_("Song and instruments..."), self.context_menu_song); menu_item.triggered.connect(self.main.on_song_prop); self.context_menu_song.addAction(menu_item)
    
    self.context_menu_note = qtwidgets.QMenu()
    menu_item = qtwidgets.QAction(_("Edit note..."      ), self.context_menu_note); menu_item.triggered.connect(self.main.on_note_prop      ); self.context_menu_note.addAction(menu_item)
    menu_item = qtwidgets.QAction(_("Edit bar..."       ), self.context_menu_note); menu_item.triggered.connect(self.main.on_bars_prop      ); self.context_menu_note.addAction(menu_item)
    menu_item = qtwidgets.QAction(_("Edit instrument..."), self.context_menu_note); menu_item.triggered.connect(self.main.on_instrument_prop); self.context_menu_note.addAction(menu_item)
    
    self.update_mesure_size()
    
  def config_listener(self, obj, type, new, old):
    for drawer in self.drawers:
      drawer.config_listener(obj, type, new, old)
    if type is object:
      if   (new.get("FONTSIZE") != old.get("FONTSIZE")):
        if globdef.config.FONTSIZE:
          self.set_default_font_size(globdef.config.FONTSIZE)
        else:
          self.set_default_font_size(self.get_style().font_desc.get_size() / pango.SCALE * pangocairo.cairo_font_map_get_default().get_resolution() / 72.0)
        self.reset()
        self.need_update_selection = 1
        self.render_all()
        
  def play_tracker(self, time):
    if time == -1:
      self.render_selection()
      
      self.selection_x1     = 1000000
      self.selection_y1     = 1000000
      self.selection_x2     = -1
      self.selection_y2     = -1
      for note in self.selections:
        drawer = self.partition_2_drawer[note.partition]
        x1, y1, x2, y2 = drawer.note_dimensions(note)

        x1 += self.x
        y1 += self.y
        x2 += self.x
        y2 += self.y
        if x1 < self.selection_x1: self.selection_x1 = x1
        if y1 < self.selection_y1: self.selection_y1 = y1
        if x2 > self.selection_x2: self.selection_x2 = x2
        if y2 > self.selection_y2: self.selection_y2 = y2
        
      self.render_selection()
      self.x_before_tracking = -1
      
    else:
      if self.x_before_tracking == -1: self.x_before_tracking = max(0, self.x)
      self.render_selection()
      self.selection_x1 = self.time_2_x(time) + self.x
      self.selection_y1 = self.drawers[1].y + self.y
      self.selection_x2 = self.selection_x1 + 2 * self.char_h_size
      self.selection_y2 = self.drawers[-1].y + self.drawers[-1].height + self.y
      self.render_selection()
      
      if self.horizontalScrollBar().maximum()  > 0: #self.horizontalScrollBar().pageStep():
        if   self.selection_x2 > self.x + self.width * 0.75:
          self.horizontalScrollBar().setValue(min(self.horizontalScrollBar().maximum(), int(self.selection_x2 - self.width * 0.1)))
        elif self.selection_x1 < self.x:
          self.horizontalScrollBar().setValue(max(0, int(self.selection_x2 - self.width * 0.1)))
          
  def destroy(self):
    if self.drawers:
      for drawer in self.drawers: drawer.destroy()
    unobserve(self.cursor)
    unobserve(self.song                        , self.song_listener)
    unobserve(self.song.playlist               , self.playlist_listener)
    unobserve(self.song.playlist.playlist_items, self.playlist_listener)
    unobserve(self.song.mesures                , self.mesures_listener)
    unobserve(self.song.partitions             , self.partitions_listener)
    
    for mesure in self.song.mesures:
      unobserve(mesure, self.mesure_listener)
      
    for partition in self.song.partitions:
      unobserve(partition, self.partition_listener)
      if isinstance(partition, model.Partition):
        unobserve_tree(partition.view, self.view_listener, find_view_children)
        unobserve(partition.notes, self.notes_listener)
        for note in partition.notes:
          unobserve(note, self.note_listener)
          
    qtwidgets.QAbstractScrollArea.destroy(self)
    
  def update_time(self):
    for drawer in self.drawers:
      if isinstance(drawer, LyricsDrawer): drawer.update_melody()
        
  def get_selected_time(self):
    if self.selections     : return list(self.selections     )[0].time
    if self.last_selections: return list(self.last_selections)[0].time
    return 0
  
  def get_selected_mesures(self):
    mesures = list(set([self.song.mesure_at(note.time) for note in self.selections]))
    mesures.sort() # Sort and reverse => if the user reduces the length of several mesures,
    mesures.reverse() # the change is first applied at the last mesure;
    # because if new mesures are created, there are created by cloning the last one.
    return mesures
    return list(set([self.song.mesure_at(note.time) for note in self.selections]))
  
  def get_selected_partitions(self):
    return list(set([note.partition for note in self.selections]))
  
  def song_listener(self, song, type, new, old):
    self.main.window.setWindowTitle("Songwrite3 -- %s" % song.title)
    self.render_all()
    
  def playlist_listener(self, obj, type, new, old):
    if type is list:
      new = set(new)
      old = set(old)
      for item in new - old: observe  (item, self.playlist_listener)
      for item in old - new: unobserve(item, self.playlist_listener)
      
    self.song.rythm_changed()
    
    self.update_mesure_size()
    self.render_all()
    
  def mesures_listener(self, obj, type, new, old):
    new = set(new)
    old = set(old)
    for mesure in new - old: observe  (mesure, self.mesure_listener)
    for mesure in old - new: unobserve(mesure, self.mesure_listener)
    self.update_mesure_size()
    
  def mesure_listener(self, mesure, type, new, old):
    self.update_mesure_size()
    self.render_all()
    
  def partitions_listener(self, obj, type, new, old):
    new = set(new)
    old = set(old)
    for partition in new - old:
      observe  (partition, self.partition_listener)
      if isinstance(partition, model.Partition):
        observe_tree(partition.view , self.view_listener, find_view_children)
        observe(partition.notes, self.notes_listener)
        for note in partition.notes: observe(note, self.note_listener)
        
    for partition in old - new:
      unobserve(partition, self.partition_listener)
      if isinstance(partition, model.Partition):
        unobserve_tree(partition.view , self.view_listener, find_view_children)
        unobserve(partition.notes, self.notes_listener)
        for note in partition.notes: unobserve(note, self.note_listener)
        
    self.update_melody_lyrics()
    for drawer in self.drawers: drawer.drawers_changed()
    self.deselect_all()
    self.reset()
    self.render_all()
    
  def update_melody_lyrics(self):
    current_melody = None
    for drawer in self.drawers:
      if   isinstance(drawer, LyricsDrawer):
        if current_melody: current_melody.associated_lyrics.append(drawer)
      elif isinstance(drawer, PartitionDrawer):
        drawer.associated_lyrics = []
        if drawer.partition.view.ok_for_lyrics:
          current_melody = drawer
          
  def partition_listener(self, partition, type, new, old):
    if type is object:
      if   (new.get("view") != old.get("view")):
        unobserve_tree(old.get("view"), self.view_listener, find_view_children)
        observe_tree  (new.get("view"), self.view_listener, find_view_children)
        
        self.deselect_all()
        self.reset()
        self.render_all()
      if   (new.get("g8") != old.get("g8")) or (new.get("tonality") != old.get("tonality")):
        self.deselect_all()
        self.reset()
        self.render_all()
      elif (new.get("instrument") != old.get("instrument")) or (new.get("header") != old.get("header")) or (new.get("visible") != old.get("visible")):
        self.render_all()
        
    self.partition_2_drawer[partition].partition_listener(partition, type, new, old)
    
  def view_listener(self, view, type, new, old):
    self.render_all()
    
  def strings_listener(self, view, type, new, old):
    self.render_all()
    
  def notes_listener(self, obj, type, new, old):
    new = set(new)
    old = set(old)
    for note in new - old:
      if not isobserved(note, self.note_listener): # Can be already observed if note was the cursor before
        observe  (note, self.note_listener)
    for note in old - new: unobserve(note, self.note_listener)
    
    drawer = self.partition_2_drawer.get(tuple(new or old)[0].partition)
    if drawer:
      drawer.notes_listener(obj, type, new, old)
      
  def note_listener(self, note, type, new, old):
    #print(note, type, new, old)
    if note in self.selections:
      self.need_update_selection = 1
      if (note is self.cursor) and (note.value > 0):
        self.cursor = None
      self.render_selection()
      self.main.set_selected_note(self.main.selected_note)
    drawer = self.partition_2_drawer.get(note.partition)
    if drawer:
      drawer.note_listener(note, type, new, old)
      drawer.render_note(note)
    
  def set_cursor(self, cursor, cursor_drawer):
    self.cursor        = cursor
    self.cursor_drawer = cursor_drawer
    
  def set_zoom(self, zoom):
    self.selection_x1 = (self.selection_x1 - self.start_x) * zoom / self.zoom + self.start_x
    self.selection_x2 = (self.selection_x2 - self.start_x) * zoom / self.zoom + self.start_x
    self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value()  / self.zoom * zoom))
    self.need_update_selection = 1
    
    self.zoom = zoom
    self.render_all()
    self.update_time()
    self.main.zoom_menu.setCurrentText("%s%%" % int(zoom * 100.0))
    
  def delayed_edit(self, note):
    self._note_to_edit = note
    self.edit_timer.stop()
    self.edit_timer.start(40)
    
  def edit(self, note = None):
    note = note or self._note_to_edit
    mesures = self.get_selected_mesures()
    if len(mesures) == 1: mesure = mesures[0]
    else:                 mesure = ObjectPack(mesures)
    partitions = self.get_selected_partitions()
    if partitions:
      if len(partitions) == 1:
        partition = partitions[0]
      else:
        partition = ObjectPack(partitions)
        partition.song = ObjectPack([p.song for p in partitions])
      self.main.set_selected_partition(partition)
      
    self.main.set_selected_mesure(mesure)
    self.main.set_selected_note(note)
    
          
  def arrange_selection_at_fret(self, fret):
    old_string_ids = dict([(note, note.string_id) for note in self.selections if hasattr(note, "string_id")])
    def do_it():
      for note, string_id in old_string_ids.items():
        if isinstance(note.partition.view, model.TablatureView):
          strings = note.partition.view.strings
          if note.value - strings[string_id].base_note - note.partition.capo < fret:
            while (string_id < len(strings) - 1) and (note.value - strings[string_id].base_note - note.partition.capo < fret):
              string_id += 1
          else:
            while (string_id > 0) and (note.value - strings[string_id - 1].base_note - note.partition.capo >= fret):
              string_id -= 1
          note.string_id = string_id
      self.render_all()
      
    def undo_it():
      for note, string_id in old_string_ids.items():
        note.string_id = string_id
      self.render_all()
    UndoableOperation(do_it, undo_it, _("arrange at fret #%s") % fret, self.main.undo_stack)
    
    
  def select_all(self):
    self.deselect_all()
    for partition in self.song.partitions:
      if isinstance(partition, model.Partition):
        drawer = self.partition_2_drawer[partition]
        for note in partition.notes:
          self.add_selection(note, render = 0, edit = 1, *drawer.note_dimensions(note))
    self.render_selection()
    
  def deselect_all(self):
    if self.cursor: self.cursor_drawer.destroy_cursor()
    if self.selection_x2 != -1:
      self.render_selection() # Note: rendering is delayed
      self.selection_x1     = 1000000
      self.selection_y1     = 1000000
      self.selection_x2     = -1
      self.selection_y2     = -1
    self.selections      = set()
    self.cursor          = None
    self.previous_text   = ""
    self.touchscreen_new_note = None
    
  def extend_selection(self, x1, y1, x2, y2, note = None):
    if self.selection_x1 > x1:
      self.selection_x1 = x1
      if note and (note.time == 0):
        self.horizontalScrollBar().setValue(0)
      else:
        if x1 < self.x + self.start_x: self.horizontalScrollBar().setValue(int(x1 - self.start_x))
        
    if self.selection_y1 > y1:
      self.selection_y1 = y1
      if y1 < self.y: self.verticalScrollBar().setValue(int(y1))
      
    if self.selection_x2 < x2:
      self.selection_x2 = x2
      if x2 > self.x + self.width: self.horizontalScrollBar().setValue(int(x2 - self.width))
        
    if self.selection_y2 < y2:
      self.selection_y2 = y2
      if y2 > self.y + self.height: self.verticalScrollBar().setValue(int(y2 - self.height))
      
  def add_selection(self, note, x1, y1, x2, y2, render = 1, edit = 1):
    self.selections.add(note)
    self.extend_selection(x1 + self.x, y1 + self.y, x2 + self.x, y2 + self.y, note)
    
    if not note is self.cursor:
      global CLIPBOARD, CLIPBOARD_SOURCE, CLIPBOARD_X1, CLIPBOARD_Y1, CLIPBOARD_X2, CLIPBOARD_Y2
      CLIPBOARD_SOURCE = self
      CLIPBOARD        = self.last_selections   = self.selections
      CLIPBOARD_X1     = self.last_selection_x1 = self.selection_x1
      CLIPBOARD_Y1     = self.last_selection_y1 = self.selection_y1
      CLIPBOARD_X2     = self.last_selection_x2 = self.selection_x2
      CLIPBOARD_Y2     = self.last_selection_y2 = self.selection_y2
      
      #CLIPBOARD2.set_with_data([(CLIPBOARD2_NAME, 0, 0)], self.clipboard_get, self.clipboard_clear, None)
    if render: self.render_selection()
    if edit  : self.delayed_edit(note)
    
  def clipboard_clear(self, clipboard, userdata): pass
  
  def clipboard_get(self, clipboard, selection_data, info, userdata):
    _xml    = StringIO()
    xml     = codecs.lookup("utf8")[3](_xml)
    context = model._XMLContext()
    xml.write("""<?xml version="1.0" encoding="utf-8"?>\n<notes click_x="0">""")
    
    min_y = 10000.0
    for note in CLIPBOARD:
      drawer = self.partition_2_drawer[note.partition]
      x1, y1, x2, y2 = drawer.note_dimensions(note)
      y = (y1 + y2) // 2
      if y < min_y: min_y = y
      
    for note in CLIPBOARD:
      drawer = self.partition_2_drawer[note.partition]
      x1, y1, x2, y2 = drawer.note_dimensions(note)
      nb_char = len(drawer.note_text(note))
      x = x1 + (self.char_h_size * nb_char) // 2 - CLIPBOARD_X1
      y = (y1 + y2) // 2 - min_y
      label = drawer.strings[note.partition.view.note_string_id(note)].value_2_text(note)
      note.__xml__(xml, context, ' x="%r" y="%r" label="%s" view_type="%s"' % (x, y, label, note.partition.view.__class__.__name__[:-4].lower()))
    xml.write("</notes>")
    
    selection_data.set(selection_data.target, 8, xml.getvalue())
    
  def mouseMoveEvent(self, event):
    try: self.on_mouse_motion(event)
    except: sys.excepthook(*sys.exc_info())
    
  def mousePressEvent(self, event):
    try: self.on_button_press(event)
    except: sys.excepthook(*sys.exc_info())
    
  def mouseReleaseEvent(self, event):
    try: self.on_button_release(event)
    except: sys.excepthook(*sys.exc_info())

  def mouseDoubleClickEvent(self, event):
    try: self.on_button_doubleclick(event)
    except: sys.excepthook(*sys.exc_info())
    
  def wheelEvent(self, event):
    try: self.on_mouse_wheel(event)
    except: sys.excepthook(*sys.exc_info())
    
  def on_mouse_wheel(self, event):
    if event.modifiers() == qtcore.Qt.ControlModifier:
      delta = event.angleDelta().y()
      if   delta < 0: self.change_zoom(-1)
      elif delta > 0: self.change_zoom( 1)
    else:
      qtwidgets.QAbstractScrollArea.wheelEvent(self, event)
      
  def on_mouse_motion(self, event):
    if   self.touchscreen_new_note:
      drawer = self.partition_2_drawer[self.touchscreen_new_note.partition]
      value  = self.touchscreen_new_note_value0
      delta  = int((self.touchscreen_new_note_y0 - event.y()) // (20.0 * self.scale))
      value  = drawer.mouse_motion_note(value, delta)
      while not drawer.note_value_possible(self.touchscreen_new_note, value):
        if delta >= 0: value += 1
        else:          value -= 1
      if self.touchscreen_new_note.value != value:
        self.touchscreen_new_note.value = value
        scan()
        
    elif (self.current_button == qtcore.Qt.LeftButton) and ((event.pos() - self.drag_start_position).manhattanLength() >= qtwidgets.QApplication.startDragDistance()):
      if self.selections and (self.selection_x1 <= self.click_x <= self.selection_x2) and (self.selection_y1 <= self.click_y <= self.selection_y2) and not self.cursor:
        width  = int(self.selection_x2 - self.selection_x1) + 2
        height = int(self.selection_y2 - self.selection_y1) + 2
        pixmap = self.draw_drag_icon(self.selection_x1 - 1, self.selection_y1 - 1, width, height)
        
        mime_data = SongwriteMimeData(self, self.last_selections, self.click_x, self.click_y)
        drag = qtgui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(qtcore.QPoint(int(self.click_x - self.selection_x1), int(self.click_y - self.selection_y1)))
        
        drop_action = drag.exec(qtcore.Qt.CopyAction | qtcore.Qt.MoveAction)
        if drop_action == qtcore.Qt.MoveAction:
          # Some notes in the selection may have been already deleted, if the selection was pasted partly
          # over the selection itself.
          notes = [note for note in mime_data.notes if note.partition and note in note.partition.notes]
          if notes: self.delete_notes(notes)
          if (drag.target() is self) or (drag.target() is self.viewport()):
            if len(mime_data.notes) == 1: action_name = _("move one note")
            else:                         action_name = _("move %s notes") % len(mime_data.notes)
            if notes: self.main.undo_stack.merge_last_operations(action_name)
      else:
        if self.selections: self.deselect_all()
        old_sel_x1 = self.selection_x1
        old_sel_y1 = self.selection_y1
        old_sel_x2 = self.selection_x2
        old_sel_y2 = self.selection_y2
        if   event.x() <= self.start_x: self.horizontalScrollBar().setValue(max(0, self.horizontalScrollBar().value() - 10))
        elif event.x() >= self.width  : self.horizontalScrollBar().setValue(min(max(self.horizontalScrollBar().maximum(), 0), self.horizontalScrollBar().value() + 10))
        if   event.y() <= 0           : self.verticalScrollBar().setValue(max(0, self.verticalScrollBar().value() - 10))
        elif event.y() >= self.height : self.verticalScrollBar().setValue(min(max(self.verticalScrollBar().maximum(), 0), self.verticalScrollBar().value() + 10))
        self.selection_x1 = max(min(self.click_x, event.x() + self.x), self.start_x)
        self.selection_y1 = min(self.click_y, event.y() + self.y)
        self.selection_x2 = max(self.click_x, event.x() + self.x)
        self.selection_y2 = max(self.click_y, event.y() + self.y)
        self.render(min(old_sel_x1, self.selection_x1) - 1,
                    min(old_sel_y1, self.selection_y1) - 1,
                    max(old_sel_x2, self.selection_x2) - min(old_sel_x1, self.selection_x1) + 2,
                    max(old_sel_y2, self.selection_y2) - min(old_sel_y1, self.selection_y1) + 2)
        
  def on_button_press(self, event):
    self.setFocus(qtcore.Qt.MouseFocusReason)
    self.click_x = event.x() + self.x
    self.click_y = event.y() + self.y
    self.current_button = event.button()
    if   event.button() == qtcore.Qt.LeftButton:
      self.drag_start_position = event.pos()
      if self.selections and (self.selection_x1 <= self.click_x <= self.selection_x2) and (self.selection_y1 <= self.click_y <= self.selection_y2):
        if self.cursor in self.selections:
          drawer = self.partition_2_drawer[list(self.selections)[0].partition]
          if drawer.on_touchscreen_new_note(event):
            self.touchscreen_new_note        = tuple(self.selections)[0]
            self.touchscreen_new_note_y0     = event.y()
            self.touchscreen_new_note_value0 = self.touchscreen_new_note.value
      else:
        self.deselect_all()
        if event.x() > self.start_x:
          for drawer in self.drawers:
            if drawer.y <= event.y() <= drawer.y + drawer.height:
              drawer.on_button_press(event)
              break
            
    elif event.button() == qtcore.Qt.MidButton:
      if CLIPBOARD:
        mime_data = SongwriteMimeData(CLIPBOARD_SOURCE, CLIPBOARD, CLIPBOARD_X1 + 20, CLIPBOARD_Y1 + 20)
        
        if mime_data.hasFormat(SONGWRITE_MIME_TYPE):
          width  = int(CLIPBOARD_X2 - CLIPBOARD_X1) + 2
          height = int(CLIPBOARD_Y2 - CLIPBOARD_Y1) + 2
          pixmap = CLIPBOARD_SOURCE.draw_drag_icon(CLIPBOARD_X1 - 1, CLIPBOARD_Y1 - 1, width, height)
          
          drag = qtgui.QDrag(self)
          drag.setMimeData(mime_data)
          drag.setPixmap(pixmap)
          drag.setHotSpot(qtcore.QPoint(20, 20))
          
          drop_action = drag.exec(qtcore.Qt.CopyAction)
          
    elif event.button() == qtcore.Qt.RightButton:
      if event.x() > self.start_x:
        for drawer in self.drawers:
          if drawer.y <= event.y() <= drawer.y + drawer.height: drawer.on_button_press(event)
          
  def on_button_doubleclick(self, event):
    if event.button() == qtcore.Qt.LeftButton:
      for drawer in self.drawers:
        if   drawer.y <= event.y() <= drawer.y + drawer.height:
          if isinstance(drawer, SongDrawer):
            self.main.set_selected_partition(None)
            self.main.on_song_prop()
          else:
            if event.x() < self.start_x:
              self.main.set_selected_partition(getattr(drawer, "partition", None) or getattr(drawer, "lyrics", None))
              self.main.on_instrument_prop()
          break
        
  def on_button_release(self, event):
    if (not self.selections) and (self.selection_x2 != -1):
      time1 = self.x_2_time(self.selection_x1 - self.x)
      time2 = self.x_2_time(self.selection_x2 - self.x)
      y1 = self.selection_y1 - self.y
      y2 = self.selection_y2 - self.y
      
      self.deselect_all()
      for partition in self.song.partitions:
        if not isinstance(partition, model.Partition): continue
        drawer = self.partition_2_drawer[partition]
        string_id1 = drawer.y_2_string_id(y1 + drawer.string_height // 2, 1)
        string_id2 = drawer.y_2_string_id(y2 - drawer.string_height // 2, 1)
        
        for note in partition.notes_at(time1, time2):
          if string_id1 <= drawer.note_string_id(note) <= string_id2:
            self.add_selection(note, render = 0, edit = 0, *drawer.note_dimensions(note))
            
      if self.selections:
        self.render_selection()
        if len(self.selections) == 1:
          self.delayed_edit(tuple(self.selections)[0])
        else:
          pack = ObjectPack(list(self.selections))
          self.delayed_edit(pack)
          
    self.current_button = 0
    
  def dragEnterEvent(self, event):
    if event.mimeData().hasFormat(SONGWRITE_MIME_TYPE): event.acceptProposedAction()
    
  def dragMoveEvent(self, event):
    if event.mimeData().hasFormat(SONGWRITE_MIME_TYPE): event.acceptProposedAction()
    
  def dropEvent(self, event):
    x0, y0 = event.pos().x(), event.pos().y()
    xml = event.mimeData().data(SONGWRITE_MIME_TYPE).data().decode("utf8")
    click_x, notes = stemml.parse(StringIO(xml))
    
    orig_time = click_x / self.zoom
    dest_time = self.x_2_time(x0)

    self.paste_notes(notes, dest_time, orig_time, y0)
    event.acceptProposedAction()
    
  def on_drag_data_get(self, notes, drag_start_x, drag_start_y):
    xml    = StringIO()
    context = model._XMLContext()
    xml.write("""<?xml version="1.0" encoding="utf-8"?>\n<notes click_x="%s">\n""" % (drag_start_x - self.selection_x1))
    
    for note in sorted(notes):
      drawer = self.partition_2_drawer[note.partition]
      x1, y1, x2, y2 = drawer.note_dimensions(note)
      nb_char = len(drawer.note_text(note))
      x = x1 + (self.char_h_size * nb_char) // 2 - drag_start_x
      y = (y1 + y2) // 2 - drag_start_y + self.y
      label = drawer.strings[note.partition.view.note_string_id(note)].value_2_text(note)
      note.__xml__(xml, context, ' x="%r" y="%r" label="%s" view_type="%s"' % (x, y, label, note.partition.view.__class__.__name__[:-4].lower()))
    xml.write("</notes>")
    return xml.getvalue()
    
  def on_copy(self):
    mime_data = SongwriteMimeData(self, self.selections, self.selection_x1 + 20, self.selection_y1 + 20)
    mime_data.generate_xml() # Pre-generates XML now
    qtwidgets.QApplication.clipboard().setMimeData(mime_data)
    
  def on_cut(self):
    self.on_copy()
    self.delete_notes(self.selections)
    
  def on_paste(self):
    if not self.selections: return # Don't know where to paste
    mime_data = qtwidgets.QApplication.clipboard().mimeData()
    if mime_data.hasFormat(SONGWRITE_MIME_TYPE):
      xml = mime_data.data(SONGWRITE_MIME_TYPE).data().decode("utf8")
      click_x, notes = stemml.parse(StringIO(xml))
      note      = tuple(self.selections)[0]
      drawer    = self.partition_2_drawer[note.partition]
      y0        = drawer.string_id_2_y(drawer.note_string_id(note))
      dest_time = note.time
      orig_time = 0
      self.paste_notes(notes, dest_time, orig_time, y0)
      
  def paste_notes(self, notes, dest_time, orig_time, y0):
    orig_time += min([note.time for note in notes])
    
    clip_duration = ZOOM_2_CLIP_DURATION[self.zoom]
    if clip_duration ==  96:
      if (self.song.mesure_at(dest_time) or self.song.mesures[-1]).rythm2 == 8: clip_duration /= 2
    if clip_duration == 144:
      if (self.song.mesure_at(dest_time) or self.song.mesures[-1]).rythm2 == 4: clip_duration /= 3
    else:
      if clip_duration / 1.5 in model.DURATIONS.keys(): clip_duration /= 3
      
    dt = int(0.4 + float(abs(dest_time - orig_time)) / clip_duration) * clip_duration
    if dest_time < orig_time: dt = -dt
    
    notes_data     = []
    previous_notes = {}
    for note in notes:
      y = y0 + note.y
      drawer = self.y_2_drawer(y)

      if not isinstance(drawer, PartitionDrawer): continue
      time = note.time + dt
      if time < 0: continue
      
      if (note.view_type == drawer.partition.view.__class__.__name__[:-4].lower()) and drawer.partition.view.can_paste_note_by_string:
        # Paste by string
        string_id = drawer.y_2_string_id(y)
        if string_id is None: continue
        paste_by_string = 1
      else:
        # Paste by note
        string_id = drawer.partition.view.note_string_id(note)
        paste_by_string = 0
        
      notes_data.append((note, drawer, time, string_id, paste_by_string))
      for previous_note in drawer.partition.notes_at(time):
        if string_id == drawer.note_string_id(previous_note):
          drawer_previous_notes = previous_notes.get(drawer)
          if not drawer_previous_notes: drawer_previous_notes = previous_notes[drawer] = []
          drawer_previous_notes.append(previous_note)
          break
        
    saved_duration = {}
    def do_it(notes_data = notes_data):
      for drawer, notes in previous_notes.items():
        drawer.partition.remove(*notes)
        
      new_notes = {}
      for note, drawer, time, string_id, paste_by_string in notes_data:
        new_note = model.Note(drawer.partition, time, note.duration, note.value, note.volume)
        new_note.fx           = note.fx
        new_note.link_fx      = note.link_fx
        new_note.duration_fx  = note.duration_fx
        new_note.strum_dir_fx = note.strum_dir_fx
        if note.bend_pitch: new_note.bend_pitch = note.bend_pitch
        for attr in model.NOTE_ATTRS:
          value = getattr(note, attr)
          if not value is None: setattr(new_note, attr, value)
          
        if not drawer.partition.view.automatic_string_id:
          new_note.string_id = string_id
        if paste_by_string:
          note.partition = drawer.partition # required for text_2_value
          new_note.value = drawer.strings[string_id].text_2_value(new_note, note.label)
          
          
        drawer_new_notes = new_notes.get(drawer)
        if not drawer_new_notes: drawer_new_notes = new_notes[drawer] = []
        drawer_new_notes.append(new_note)
        
      self.deselect_all()
      
      for drawer, notes in new_notes.items():
        drawer.partition.add_note(*notes)
        
        for note in notes:
          self.add_selection(note, render = 0, edit = 0, *drawer.note_dimensions(note))
          
        self.auto_update_duration(min(notes), saved_duration)
        self.auto_update_duration(drawer.partition.note_after(max(notes)))

      self.render_all()
      
    def undo_it(notes = notes):
      new_notes = {}
      for note, drawer, time, string_id, paste_by_string in notes_data:
        drawer_new_notes = new_notes.get(drawer)
        if not drawer_new_notes: drawer_new_notes = new_notes[drawer] = []
        for new_note in drawer.partition.notes_at(time):
          
          if paste_by_string:
            if string_id == drawer.note_string_id(new_note):
              drawer_new_notes.append(new_note)
              break
          else:
            if new_note.value == note.value:
              drawer_new_notes.append(new_note)
              break
            
      for drawer, notes in new_notes.items(): drawer.partition.remove(*notes)
        
      for drawer, notes in previous_notes.items(): drawer.partition.add_note(*notes)
        
      self.restore_saved_duration(saved_duration)
      self.render_all()
      
    if len(notes) == 1: action_name = _("paste one note")
    else:               action_name = _("paste %s notes") % len(notes)
    UndoableOperation(do_it, undo_it, action_name, self.main.undo_stack)
    
  def round_time_to_current_duration(self, time, delta = 0):
    if   int(self.current_duration * 1.5) in model.DURATIONS: # Triolet
      duration = self.current_duration
      
    elif int(self.current_duration / 1.5) in model.DURATIONS: # Pointe
      duration = min(ZOOM_2_CLIP_DURATION[self.zoom], int(self.current_duration / 3))
      
    else:
      duration = min(ZOOM_2_CLIP_DURATION[self.zoom], self.current_duration)
      
      if (self.current_duration == 96) and ((self.song.mesure_at(time) or self.song.mesures[-1]).rythm2 == 8):
        duration /= 2
        
    return max(0, int((delta + (time // duration)) * duration))
  
  def keyPressEvent(self, event):
    try: self.on_key_press(event)
    except: sys.excepthook(*sys.exc_info())
    
  def on_key_press(self, event):
    keyval = event.key()
    if   keyval == qtcore.Qt.Key_Left:
      if self.selections:
        sel = tuple(self.selections)[0]
        time = sel.time
        string_id = self.note_string_id(sel)
        note = sel.partition.note_before_pred(sel, lambda a: self.note_string_id(a) == string_id)
        time0 = self.round_time_to_current_duration(time, -1)
        if note and note.time >= time0:
          self.deselect_all()
          self.partition_2_drawer[sel.partition].select_note(note)
        elif time > 0:
          self.deselect_all()
          self.partition_2_drawer[sel.partition].select_at(time0, string_id)
          
    elif keyval == qtcore.Qt.Key_Right:
      if self.selections:
        sel = tuple(self.selections)[0]
        time = sel.time
        string_id = self.note_string_id(sel)
        note = sel.partition.note_after_pred(sel, lambda a: self.note_string_id(a) == string_id)
        time0 = self.round_time_to_current_duration(time, 1)
        if note and note.time <= time0:
          self.deselect_all()
          self.partition_2_drawer[sel.partition].select_note(note)
        else:
          self.deselect_all()
          self.partition_2_drawer[sel.partition].select_at(time0, string_id)
          
    elif keyval == qtcore.Qt.Key_Up:
      if self.selections:
        sel = tuple(self.selections)[0]
        string_id = self.note_string_id(sel)
        if string_id > 0:
          self.deselect_all()
          self.partition_2_drawer[sel.partition].select_at(sel.time, string_id - 1)
        else:
          i = self.drawers.index(self.partition_2_drawer[sel.partition])
          if i > 0:
            drawer = self.drawers[i - 1]
            if isinstance(drawer, PartitionDrawer):
              self.deselect_all()
              drawer.select_at(sel.time, len(drawer.strings) - 1)
              
    elif keyval == qtcore.Qt.Key_Down:
      if self.selections:
        sel = tuple(self.selections)[0]
        string_id = self.note_string_id(sel)
        if string_id < len(self.partition_2_drawer[sel.partition].strings) - 1:
          self.deselect_all()
          self.partition_2_drawer[sel.partition].select_at(sel.time, string_id + 1)
        else:
          i = self.drawers.index(self.partition_2_drawer[sel.partition])
          if i < len(self.drawers) - 1:
            drawer = self.drawers[i + 1]
            if isinstance(drawer, PartitionDrawer):
              self.deselect_all()
              drawer.select_at(sel.time, 0)
              
    elif keyval == qtcore.Qt.Key_Home:
      if self.selections:
        note   = list(self.selections)[0]
        drawer = self.partition_2_drawer[note.partition]
        string_id = drawer.note_string_id(note)
        self.deselect_all()
        drawer.select_at(0, string_id)
        
    elif keyval == qtcore.Qt.Key_End:
      if self.selections:
        note   = list(self.selections)[0]
        drawer = self.partition_2_drawer[note.partition]
        string_id = drawer.note_string_id(note)
        self.deselect_all()
        drawer.select_at(self.song.mesures[-1].end_time() - self.current_duration, string_id)
        
    elif (keyval == qtcore.Qt.Key_Asterisk) or (keyval == qtcore.Qt.Key_multiply): # *
      self.main.set_duration_longer()
    elif (keyval == qtcore.Qt.Key_Slash) or (keyval == qtcore.Qt.Key_Colon): # / or :
      self.main.set_duration_shorter()
      
    elif (keyval == qtcore.Qt.Key_Period): # .
      self.toggle_dotted()
      
    elif (keyval == qtcore.Qt.Key_Delete) or (keyval == qtcore.Qt.Key_Backspace):
      if self.selections: self.delete_notes(self.selections)
      
    else:
      if self.selections:
        drawers = list(set([self.partition_2_drawer[note.partition] for note in self.selections]))
        if len(drawers) == 1:
          if drawers[0].on_key_press(event): return
          
      if   (keyval == qtcore.Qt.Key_Plus) or (keyval == qtcore.Qt.Key_Equal): # + ou =
        self.shift_selections_values(1)
        
      elif (keyval == qtcore.Qt.Key_Minus): # -
        self.shift_selections_values(-1)
        
      elif (qtcore.Qt.Key_0 <= keyval <= qtcore.Qt.Key_9): # Numbers
        nb = keyval - qtcore.Qt.Key_0
        self.previous_text += str(nb)
        self.on_number_typed(self.previous_text)
        
      elif keyval == qtcore.Qt.Key_Agrave:
        self.previous_text += "0"
        self.on_number_typed(self.previous_text)
        
      elif (keyval == qtcore.Qt.Key_AsciiCircum) or (keyval == qtcore.Qt.Key_Dead_Circumflex): # ^
        if self.selections: self.set_selections_strum_dir_fx("up")
        
      elif keyval == qtcore.Qt.Key_Underscore: # _
        if self.selections: self.set_selections_strum_dir_fx("down")

      elif keyval == qtcore.Qt.Key_Comma: # ,
        if self.selections: self.set_selections_strum_dir_fx("down_thumb")

      elif keyval == qtcore.Qt.Key_L:
        if self.selections: self.set_selections_link_fx("link")

      elif keyval == qtcore.Qt.Key_P:
        if self.selections: self.set_selections_duration_fx("fermata")

      elif keyval == qtcore.Qt.Key_H:
        if self.selections: self.set_selections_fx("harmonic")

      elif keyval == qtcore.Qt.Key_D:
        if self.selections: self.set_selections_fx("dead")

      elif keyval == qtcore.Qt.Key_T:
        if self.selections: self.set_selections_fx("tremolo")

      elif keyval == qtcore.Qt.Key_B:
        if self.selections: self.set_selections_fx("bend")

      elif keyval == qtcore.Qt.Key_S:
        if self.selections: self.set_selections_link_fx("slide")

      elif keyval == qtcore.Qt.Key_R:
        if self.selections: self.set_selections_fx("roll")

      elif keyval == qtcore.Qt.Key_N:
        if self.selections: self.remove_selections_fx()

      elif (keyval == qtcore.Qt.Key_Return) or (keyval == qtcore.Qt.Key_Enter): # return
        self.toggle_accent()

      elif keyval == qtcore.Qt.Key_Q:
        self.main.on_close()

      #elif keyval == qtcore.Qt.Key_Space:
      #  self.main.on_play_from_here()

      #elif (keyval == qtcore.Qt.Key_V) and (event.state & gtk.gdk.CONTROL_MASK): # C-V
      elif event.matches(qtgui.QKeySequence.Copy): # C-C
        self.on_copy()

      elif event.matches(qtgui.QKeySequence.Cut): # C-X
        self.on_cut()

      elif event.matches(qtgui.QKeySequence.Paste): # C-V
        self.on_paste()

      #elif (keyval == qtcore.Qt.Key_A) and (event.state & gtk.gdk.CONTROL_MASK): # C-A
      elif event.matches(qtgui.QKeySequence.SelectAll): # C-A
        self.select_all()

      elif keyval == qtcore.Qt.Key_A: # a
        if self.selections: self.set_selections_duration_fx("appoggiatura")
        
      elif event.matches(qtgui.QKeySequence.Undo): # C-Z
        self.main.on_undo()
        
      elif event.matches(qtgui.QKeySequence.Redo): # C-Y
        self.main.on_redo()
        
        
  def auto_update_duration(self, note, save = None):
    if globdef.config.AUTOMATIC_DURATION and note:
      previous_notes = note.partition.notes_before(note)

      appo = previous_notes and previous_notes[0].duration_fx == "appoggiatura"
      for previous_note in previous_notes:
        next = previous_note.partition.note_after(previous_note)
        if not appo:
          while next and next.duration_fx == "appoggiatura": next = previous_note.partition.note_after(next)
        if next:
          new_duration = int(next.time - previous_note.time)
          if new_duration in model.VALID_DURATIONS:
            if (not save is None) and (not previous_note in save): save[previous_note] = previous_note.duration
            previous_note.duration = new_duration
            
      if appo:
        self.auto_update_duration(previous_notes[0])
        
  def restore_saved_duration(self, save):
    for note, duration in save.items(): note.duration = duration
    save.clear()
    
  def on_number_typed(self, text):
    notes = list(self.selections)
    if notes:
      old_values = [note.value for note in notes]
      
      new_values = []
      for note in notes:
        drawer = self.partition_2_drawer[note.partition]
        new_values.append(drawer.strings[drawer.note_string_id(note)].text_2_value(note, text))
        
      drawer = self.partition_2_drawer[notes[0].partition]
      player.play_note(notes[0].partition.instrument,
                       drawer.strings[drawer.note_string_id(notes[0])].text_2_value(notes[0], text))
      
      saved_duration = {}
      
      def do_it(notes = notes, text = text, saved_duration = saved_duration):
        for i in range(len(notes)):
          if notes[i].value < 0:
            notes[i].partition.add_note(notes[i])
            self.auto_update_duration(notes[i], saved_duration)
          notes[i].value = new_values[i]
          self.auto_update_duration(notes[i].partition.note_after(notes[i]))
      def undo_it(notes = notes, old_values = old_values, saved_duration = saved_duration):
        for i in range(len(notes)):
          new_values[i]  = notes[i].value # new values may have been changed when adding a note by touching the screen and then dragging up or down
          notes[i].value = old_values[i]
          if notes[i].value < 0: notes[i].partition.remove(notes[i])
        self.restore_saved_duration(saved_duration)
      UndoableOperation(do_it, undo_it, _("note change"), self.main.undo_stack)
      
  def shift_selections_values(self, d):
      notes      = list(self.selections)
      old_values = [note.value for note in notes]
      def do_it(notes = notes):
        for note in notes:
          drawer = self.partition_2_drawer[note.partition]
          if note.value < 0: note.partition.add_note(note)
          
          current_value = note.value
          note.value = abs(note.value) + d
          while not drawer.note_value_possible(note, note.value):
            if (note.value < 2) or (note.value > 200):
              note.value = current_value
              break
            note.value += d
          if isinstance(drawer, TablatureDrawer) and (note.value < drawer.strings[drawer.note_string_id(note)].base_note):
            note.value = drawer.strings[drawer.note_string_id(note)].base_note
            
        self.main.set_selected_note(self.main.selected_note) # Changed !
        
      def undo_it(notes = notes, old_values = old_values):
        for i in range(len(notes)):
          notes[i].value = old_values[i]
          if notes[i].value < 0: notes[i].partition.remove(notes[i])
          
        self.main.set_selected_note(self.main.selected_note) # Changed !
        
      if d > 0: UndoableOperation(do_it, undo_it, _("increase notes pitch"), self.main.undo_stack)
      else:     UndoableOperation(do_it, undo_it, _("decrease notes pitch"), self.main.undo_stack)
      
  def set_selections_volume(self, volume):
    if self.selections:
      notes      = list(self.selections)
      old_values = [note.volume for note in notes]
      def do_it(notes = notes):
        for note in notes: note.volume = volume
      def undo_it(notes = notes):
        for i in range(len(notes)): notes[i].volume = old_values[i]
      UndoableOperation(do_it, undo_it, _("change of %s") % _("volume"), self.main.undo_stack)
      
  def toggle_dotted(self, *args):
    notes      = list(self.selections)
    old_values = [note.duration for note in notes]
    def do_it(notes = notes):
      dotted = not notes[0].is_dotted()
      for note in notes:
        if note.is_dotted() != dotted:
          if dotted: note.duration = int(note.duration * 1.5)
          else:      note.duration = int(note.duration / 1.5)
      self.current_duration = notes[-1].duration
    def undo_it(notes = notes, old_values = old_values):
      for i in range(len(notes)): notes[i].duration = old_values[i]
      self.current_duration = notes[-1].duration

    UndoableOperation(do_it, undo_it, _("dotted note"), self.main.undo_stack)
    
  def toggle_triplet(self, *args):
    notes      = list(self.selections)
    old_values = [note.duration for note in notes]
    def do_it(notes = notes):
      triplet = not notes[0].is_triplet()
      for note in notes:
        if note.is_triplet() != triplet:
          if triplet: note.duration = int(note.duration * 2 / 3)
          else:       note.duration = int(note.duration * 3 / 2)
      self.current_duration = notes[-1].duration
    def undo_it(notes = notes, old_values = old_values):
      for i in range(len(notes)): notes[i].duration = old_values[i]
      self.current_duration = notes[-1].duration
      
    UndoableOperation(do_it, undo_it, _("triplet note"), self.main.undo_stack)
    
  def toggle_accent(self, *args):
    if self.selections:
      notes = list(self.selections)
      save = {}
      for note in notes: save[note] = note.volume
      def stress(notes = notes):
        for note in notes: note.volume = 255
      def unstress(notes = notes):
        for note in notes: note.volume = 204
      def restore(save = save):
        for note, volume in save.items(): note.volume = volume
      if notes[0].volume == 255: UndoableOperation(unstress, restore, _("remove accent"), self.main.undo_stack)
      else:                      UndoableOperation(stress  , restore, _("accent"), self.main.undo_stack)
      
  def delete_notes(self, notes):
    if not notes: return
    notes = list(notes)
    if notes == [self.cursor]: return
    
    saved_duration = {}
    def do_it(notes = notes):
      sel = notes[0]
      drawer = self.partition_2_drawer[sel.partition]
      partition_2_notes = {}
      for note in notes:
        l = partition_2_notes.get(note.partition)
        if not l: partition_2_notes[note.partition] = [note]
        else: l.append(note)
        drawer.render_note(note)
      for partition, notes in partition_2_notes.items():
        partition.remove(*notes)
        for note in notes: self.auto_update_duration(note, saved_duration)
      if set(notes) & self.selections:
        self.deselect_all()
        drawer.select_at(sel.time, drawer.note_string_id(sel), 0)
    def undo_it(notes = notes):
      self.deselect_all()
      partition_2_notes = {}
      for note in notes:
        l = partition_2_notes.get(note.partition)
        if not l: partition_2_notes[note.partition] = [note]
        else: l.append(note)
      for partition, notes in partition_2_notes.items():
        partition.add_note(*notes)
        drawer = self.partition_2_drawer[partition]
        for note in notes:
          self.add_selection(note, render = 0, edit = 0, *drawer.note_dimensions(note))
          drawer.render_note(note)
      self.restore_saved_duration(saved_duration)

    UndoableOperation(do_it, undo_it, _("delete %s note(s)") % len(notes), self.main.undo_stack)

  def remove_selections_fx(self):
    notes       = list(self.selections)
    old_values  = [(note.fx, note.link_fx, note.duration_fx, note.strum_dir_fx) for note in notes]
    def do_it():
      for note in notes:
        note.set_fx          ("")
        note.set_link_fx     ("")
        note.set_duration_fx ("")
        note.set_strum_dir_fx("")
    def undo_it():
      for i in range(len(notes)):
        notes[i].set_fx          (old_values[i][0])
        notes[i].set_link_fx     (old_values[i][1])
        notes[i].set_duration_fx (old_values[i][2])
        notes[i].set_strum_dir_fx(old_values[i][3])
    UndoableOperation(do_it, undo_it, _("Remove all effects"), self.main.undo_stack)
    
  def set_selections_fx(self, fx, bend_pitch = None):
    notes      = list(self.selections)
    old_values = [note.fx for note in notes]
    if not bend_pitch is None: old_bend_pitches = [note.bend_pitch for note in notes]
    def do_it():
      if fx == "bend":
        if (notes[0].fx == fx) and (notes[0].bend_pitch == bend_pitch): new_fx = ""
        else:                                                           new_fx = fx
      else:
        if notes[0].fx == fx: new_fx = ""
        else:                 new_fx = fx
      for note in notes:
        note.set_fx(new_fx)
        if not bend_pitch is None: note.bend_pitch = bend_pitch
    def undo_it():
      for i in range(len(notes)):
        notes[i].set_fx(old_values[i])
        if not bend_pitch is None:
          if old_bend_pitches[i] == 0.0: del notes[i].bend_pitch
          else:                          notes[i].bend_pitch = old_bend_pitches[i]
    UndoableOperation(do_it, undo_it, _("set special effect %s") % _(fx), self.main.undo_stack)
    
  def set_selections_link_fx(self, fx, arg = None):
    notes      = list(self.selections)
    old_values = [note.link_fx for note in notes]
    def do_it():
      if notes[0].link_fx == fx: new_fx = ""
      else:                      new_fx = fx
      for note in notes:
        note.set_link_fx(new_fx)
    def undo_it():
      for i in range(len(notes)): notes[i].set_link_fx(old_values[i])
    UndoableOperation(do_it, undo_it, _("set special effect %s") % _(fx), self.main.undo_stack)
    
  def set_selections_duration_fx(self, fx, arg = None):
    notes      = list(self.selections)
    old_values = [note.duration_fx for note in notes]
    saved_duration = {}
    def do_it():
      if notes[0].duration_fx == fx: new_fx = ""
      else:                          new_fx = fx
      for note in notes: note.set_duration_fx(new_fx)
      self.auto_update_duration(min(notes), saved_duration)
      last = max(notes)
      self.auto_update_duration(last.partition.note_after(last), saved_duration)
    def undo_it():
      for i in range(len(notes)): notes[i].set_duration_fx(old_values[i])
      self.restore_saved_duration(saved_duration)
    UndoableOperation(do_it, undo_it, _("set special effect %s") % _(fx), self.main.undo_stack)
    
  def set_selections_strum_dir_fx(self, fx, arg = None):
    if self.selections:
      notes      = list(self.selections)
      old_values = [note.strum_dir_fx for note in notes]
      def do_it(notes = notes):
        if notes[0].strum_dir_fx == fx: new_fx = ""
        else:                           new_fx = fx
        for note in notes: note.strum_dir_fx = new_fx
      def undo_it(notes = notes):
        for i in range(len(notes)): notes[i].strum_dir_fx = old_values[i]
      UndoableOperation(do_it, undo_it, _("set special effect %s") % _(fx), self.main.undo_stack)
      
  def render_pixel(self, x, y, width, height):
    self.viewport().update(int(x), int(y), int(width), int(height))
    
  def render_all(self):
    self.viewport().update()
    
  def render(self, x, y, width, height):
    self.viewport().update(int(x - self.x), int(y - self.y), int(width), int(height))
    
  def render_selection(self):
    self.viewport().update(int(self.selection_x1 - self.x) - 1, int(self.selection_y1 - self.y) - 1, max(int(self.selection_x2 - self.selection_x1) + 4, self.char_h_size * 3), int(self.selection_y2 - self.selection_y1) + 4)
    
  #def on_expose(self, obj, event):
  #  self.draw(event.area.x, event.area.y, event.area.width, event.area.height)
  #  
  #  if self.horizontalScrollBar().upper - self.horizontalScrollBar().lower < self.horizontalScrollBar().page_size:
  #    if self.horizontalScrollBar().value != 0: self.horizontalScrollBar().value = 0

  def paintEvent(self, event): # Qt paint event redefinition
    try:
      rect = event.rect()
      self.draw(rect.x(), rect.y(), rect.width(), rect.height())
    except: sys.excepthook(*sys.exc_info())
    
  def draw(self, x, y, width, height):
    #print("draw", x, y, width, height)
    self.x = self.horizontalScrollBar().value()
    self.y = self.verticalScrollBar  ().value()
    
    if self.need_update_selection:
      self.selection_x1     = 1000000
      self.selection_y1     = 1000000
      self.selection_x2     = -1
      self.selection_y2     = -1
      for note in self.selections: self.add_selection(note, render = 0, edit = 0, *self.partition_2_drawer[note.partition].note_dimensions(note))
      self.need_update_selection = 0
      
    ctx = qtgui.QPainter(self.viewport())
    ctx.setRenderHints(qtgui.QPainter.Antialiasing | qtgui.QPainter.TextAntialiasing | qtgui.QPainter.SmoothPixmapTransform)
    #ctx.setPen  (qtcore.Qt.black)
    #ctx.setBrush(qtcore.Qt.black)
    
    ctx.fillRect(int(x), int(y), int(width), int(height), qtcore.Qt.white)
    
    self.width  = self.viewport().width()
    self.height = self.viewport().height()
    
    first_drawer = None
    if not self.drawers: # first time
      self.drawers = [SongDrawer(self, self.song)]
      for partition in self.song.partitions:
        if   isinstance(partition, model.Lyrics): drawer = LyricsDrawer(self, partition)
        else:                                     drawer = partition.view.get_drawer(self)
        self.drawers.append(drawer)
        if (not first_drawer) and self.first_time:
          first_drawer = drawer
          self.first_time = 0
      self.update_melody_lyrics()
      for drawer in self.drawers: drawer.drawers_changed()
      
    if self.selection_x2 != -1:
      ctx.save()
      if self.hasFocus(): ctx.setPen(SELECTION_COLOR2)
      else:               ctx.setPen(SELECTION_COLOR)
      ctx.setBrush(SELECTION_COLOR)
      ctx.setClipRect(self.start_x - 1, 0, self.width, self.height, qtcore.Qt.IntersectClip)
      ctx.drawRoundedRect(qtcore.QRectF(self.selection_x1 - self.x, self.selection_y1 - self.y, self.selection_x2 - self.selection_x1, self.selection_y2 - self.selection_y1), 5, 5)
      ctx.restore()
      
    ctx.setBrush(qtcore.Qt.black)
    
    dy = -self.y
    total_height = 0
    for drawer in self.drawers:
      drawer.y = dy
      drawer.draw(ctx, x, y, width, height)
      dy           += drawer.height + 10
      total_height += drawer.height + 10
      
    self.horizontalScrollBar().setMaximum(max(0, int((self.song.mesures[-1].end_time() + self.song.mesures[-1].duration) * self.zoom + self.mesure_2_extra_x[self.song.mesures[-1]] - self.width)))
    self.horizontalScrollBar().setPageStep(self.width)
    self.verticalScrollBar  ().setRange(0, max(0, int(total_height - self.height)))
    self.verticalScrollBar  ().setPageStep(int(self.height))
    
    if first_drawer: first_drawer.select_at(0, 0, 0)
    
    #if (total_height <= self.height) and (self.y != 0):
    #  self.verticalScrollBar().set_value(0)
    #  self.render_all()
    
  def draw_drag_icon(self, x, y, width, height):
    _x = self.x
    _y = self.y
    self.x = x
    self.y = y
    
    image  = qtgui.QImage(width + 1, height + 1, qtgui.QImage.Format_RGB32)
    #image  = qtgui.QImage(width + 1, height + 1, qtgui.QImage.Format_ARGB32)
    image.fill(qtcore.Qt.white)
    #image.fill(qtgui.QColor(255, 255, 255, 0))
    ctx    = qtgui.QPainter(image)
    ctx.setRenderHints(qtgui.QPainter.Antialiasing | qtgui.QPainter.TextAntialiasing | qtgui.QPainter.SmoothPixmapTransform)
    
    ctx.setPen  (SELECTION_COLOR2)
    ctx.setBrush(qtcore.Qt.white)
    #ctx.setBrush(qtgui.QColor(255, 255, 255, 0))
    ctx.drawRoundedRect(qtcore.QRectF(1, 1, width - 2, height - 2), 5, 5)
    ctx.setPen  (qtcore.Qt.black)
    ctx.setBrush(qtcore.Qt.black)
    
    dy = -self.y
    for drawer in self.drawers:
      _drawer_y = drawer.y
      drawer.y = dy
      drawer.draw(ctx, 0, dy, width, height, 1)
      drawer.y = _drawer_y
      dy      += drawer.height + 10
      
    self.x = _x
    self.y = _y
    ctx.end()

    if hasattr(qtcore.Qt, "NoOpaqueDetection"): pixmap = qtgui.QPixmap.fromImage(image, qtcore.Qt.NoOpaqueDetection)
    else:                                       pixmap = qtgui.QPixmap.fromImage(image)
    #mask   = pixmap.createMaskFromColor(qtcore.Qt.white)
    #pixmap.setMask(mask)
    return pixmap
  
  def change_zoom(self, incr):
    i = zoom_levels.index(self.zoom) + incr
    if   i < 0:                    i = 0
    elif i > len(zoom_levels) - 1: i = len(zoom_levels) - 1
    self.set_zoom(zoom_levels[i])
    
  def on_before_scroll(self, obj, event):
    if event.state & gtk.gdk.CONTROL_MASK:
      if   (event.direction == gtk.gdk.SCROLL_DOWN) or (event.direction == gtk.gdk.SCROLL_LEFT):
        self.change_zoom(-1)
      else:
        self.change_zoom( 1)
      return 1
    
  #def scrollContentsBy(self, dx, dy):
  #  XXX copy and redraw only the new part ???
    
def ctx_drawStaticText(ctx, x, y, text):
  return ctx.drawStaticText(qtcore.QPointF(x, y), text)
    
def ctx_drawText(ctx, x, y, text):
  return ctx.drawText(qtcore.QPointF(x, y), text)
  
def ctx_drawText2(ctx, x, y, width, height, align, text):
  return ctx.drawText(qtcore.QRectF(x, y, width, height), align, text)

def ctx_drawLine(ctx, x1, y1, x2, y2):
  return ctx.drawLine(qtcore.QPointF(x1, y1), qtcore.QPointF(x2, y2))

def ctx_drawRect(ctx, x, y, width, height):
  return ctx.drawRect(qtcore.QRectF(x, y, width, height))
  
def ctx_drawEllipse(ctx, x, y, width, height):
  return ctx.drawEllipse(qtcore.QRectF(x, y, width, height))
  
def ctx_drawPixmap(ctx, x, y, width, height, image):
  return ctx.drawPixmap(qtcore.QRect(int(x), int(y), int(width), int(height)), image)


class Drawer(object):
  def __init__(self, canvas, compact = False):
    self.canvas  = canvas
    self.y       = 0
    self.height  = 0
    self.scale   = canvas.scale
    self.compact = compact
    
  def draw(self, ctx, x, y, width, height, drag = 0):
    return (y < self.y + self.height) and (self.y < y + height)
  
  def destroy(self): pass

  def drawers_changed(self): pass
  
  def config_listener(self, obj, type, new, old): pass
  
class SongDrawer(Drawer):
  def __init__(self, canvas, song, compact = False):
    Drawer.__init__(self, canvas, compact)
    self.song = song
    self.title_metrics   = None
    self.comment_metrics = None
    
  def on_button_press(self, event):
    if    event.button() == qtcore.Qt.RightButton:
      self.canvas.context_menu_song.popup(qtgui.QCursor.pos())
      
  def draw(self, ctx, x, y, width, height, drag = 0):
    if self.song.authors: title = "%s (%s)" % (self.song.title, self.song.authors)
    else:                 title = self.song.title
    
    if self.title_metrics:
      if title != self.title_metrics.text(): self.title_metrics.setText(title)
      if self.canvas.width != self.title_metrics.textWidth(): self.title_metrics.setTextWidth(self.canvas.width)
    else:
      self.title_metrics = qtgui.QStaticText(title)
      self.title_metrics.setTextOption(qtgui.QTextOption(qtcore.Qt.AlignHCenter))
      self.title_metrics.setTextWidth(self.canvas.width)
      self.title_metrics.prepare(font = self.canvas.title_font)
      
    ctx.setFont(self.canvas.title_font)
    title_size = self.title_metrics.size()
    ctx_drawStaticText(ctx, (self.canvas.width - title_size.width()) / 2.0, self.y + 10 * self.scale, self.title_metrics)
    ctx.setFont(self.canvas.default_font)
    
    if self.song.comments:
      # Static text do not support line break (\n)
      comment_width = self.canvas.width - int(40.0 * self.scale)
      comment_size = ctx_drawText2(ctx,
                                   20 * self.scale,
                                   self.y + title_size.height() + 10 * self.scale,
                                   comment_width, 9999,
                                   qtcore.Qt.AlignJustify | qtcore.Qt.TextWordWrap,
                                   self.song.comments)
      
      self.height = title_size.height() + comment_size.height() + 30 * self.scale
    else:
      self.height = title_size.height() + 20 * self.scale
      
    return True
  
  
class PartitionDrawer(Drawer):
  show_header       = 1
  always_draw_stems = 0
  need_extra_space_for_strum_dir = 1
  def __init__(self, canvas, partition, compact = False):
    Drawer.__init__(self, canvas, compact)
    self.partition = partition
    self.start_y   = 15 * self.scale
    self.stem_extra_height = 0
    self.stem_extra_height_bottom = 0
    self.canvas.partition_2_drawer[partition] = self
    self.note_offset_x = 0
    self.note_offset_y = 0
    if compact:
      self._draw_perfect_line = self._draw_perfect_line_pdf
      self._draw_perfect_rect = self._draw_perfect_rect_pdf
    else:
      self._draw_perfect_line = self._draw_perfect_line_pixel
      self._draw_perfect_rect = self._draw_perfect_rect_pixel
      
  def default_string_id(self, value): return 0
  
  def note_value_possible(self, note, value): return 1
  
  def mouse_motion_note(self, value, delta): return value + delta
  
  def partition_listener(self, partition, type, new, old): pass
  
  def notes_listener(self, obj, type, new, old):
    for lyrics_drawer in self.associated_lyrics: lyrics_drawer.delayed_update_melody()
    
  def note_listener(self, note, type, new, old):
    if type is object:
      if note.duration_fx != old.get("duration_fx", ""):
        for lyrics_drawer in self.associated_lyrics: lyrics_drawer.delayed_update_melody()
        
  def y_2_string_id(self, y, force = 0):
    string_id = int((y - self.y - self.stem_extra_height - self.start_y) // self.string_height)
    if not force:
      if   string_id < 0:                     return None
      elif string_id > len(self.strings) - 1: return None
    return string_id
  
  def string_id_2_y(self, string_id):
    return int(self.y + self.start_y + self.stem_extra_height + self.string_height * (string_id + 0.5))
  
  def on_key_press(self, event): return 0
  
  def on_button_press(self, event):
    if   event.button() == qtcore.Qt.LeftButton:
      string_id = self.y_2_string_id(event.y())
      if not string_id is None:
        time = self.canvas.x_2_time(event.x())
        self.select_at(time, string_id)
        
    elif event.button() == qtcore.Qt.RightButton:
      self.canvas.context_menu_note.popup(qtgui.QCursor.pos())
      
  def on_touchscreen_new_note(self, event):
    self.canvas.on_number_typed("0")
    return 1 # OK to change note by dragging up or down
  
  def select_at(self, time, string_id, fix_time = 1):
    if fix_time: time0 = self.canvas.round_time_to_current_duration(time)
    else:        time0 = time
    
    notes = self.partition.notes_at(time0, time)
    notes = [note for note in notes if self.note_string_id(note) == string_id]
    for note in notes:
      if note.end_time() > time:
        self.select_note(note)
        break
    else:
      for note in notes:
        if note.time == time0:
          self.select_note(note)
          break
      else:
        cursor = self.create_cursor(time0, self.canvas.current_duration, string_id, -self.strings[string_id].base_note)
        while cursor.time >= self.canvas.song.mesures[-1].end_time():
          mesure = self.canvas.song.add_mesure()
          self.canvas.render(self.canvas.time_2_x(mesure.time) - 10.0, 0, mesure.duration * self.canvas.zoom + 20.0, self.canvas.height)
        observe(cursor, self.canvas.note_listener)
        self.canvas.set_cursor(cursor, self)
        self.select_note(cursor)
        self.render_note(cursor)
        
  def destroy(self):
    self.destroy_cursor(render = 0)
    Drawer.destroy(self)
    
  def create_cursor(self, time, duration, string_id, value):
    cursor          = model.Note(self.partition)
    cursor.time     = time
    cursor.duration = duration
    cursor.value    = value
    return cursor
    
  def destroy_cursor(self, render = 1):
    cursor = self.canvas.cursor
    if cursor:
      unobserve(cursor)
      self.canvas.cursor        = None
      self.canvas.cursor_drawer = None
      if render: self.render_note(cursor)
      if cursor.linked_to: cursor.linked_to._link_from(None)
      
  def select_note(self, note):
    #self.canvas.add_selection(note, *self.note_dimensions(note))
    x1, y1, x2, y2 = self.note_dimensions(note)
    self.canvas.add_selection(note, x1, y1, x2 - 2, y2)
    
  def render_note(self, note):
    mesure = self.canvas.song.mesure_at(note)
    if mesure.rythm2 == 8: time1 = (note.link_start() // 144) * 144; time2 = max(note.link_end(), time1 + 144)
    else:                  time1 = (note.link_start() //  96) *  96; time2 = max(note.link_end(), time1 +  96)
    self.canvas.render_pixel(
      self.canvas.time_2_x(time1) - 10.0 * self.scale,
      self.y,
      (time2 - time1) * self.canvas.zoom + 20 * self.scale,
      self.height + self.canvas.default_line_height // 2 + self.canvas.default_ascent // 2,
      )
    
  def note_dimensions(self, note):
    x = self.canvas.time_2_x(note.time)
    y = self.string_id_2_y(self.note_string_id(note)) - self.string_height // 2
    return (
      x,
      y,
      x + max(note.duration * self.canvas.zoom, self.canvas.char_h_size * 1.5),
      y + self.string_height,
      )
  
  def note_width(self, note):
    return self.canvas.char_h_size * len(self.note_text(note))
  
  def draw_mesure(self, ctx, time, mesure, y, height, draw_bars = True):
    x = self.canvas.time_2_x(time)
    if   time == 0:
      bar_x = x - 2.0 * self.scale
      bold  = 1
    elif mesure == None:
      bar_x = x + 2.5 * self.scale
      bold  = 1
    else:
      bar_x = x - 2.0 * self.scale
      bold  = 0
    nheight = height
    symbols = self.partition.song.playlist.symbols.get(mesure)
    if symbols:
      start_repeat = start_alternative = end_repeat = False
      for symbol in symbols:
        if symbol.startswith(r"\repeat"): start_repeat = True
        elif (symbol == "} % end repeat") or (symbol == "} % end alternative"): end_repeat = True
        elif symbol.startswith(r"{ % start alternative"):
          start_alternative = True
          if (self.partition is self.canvas.song.partitions[0]) and not((self.canvas.__class__.__name__ == "PSCanvas") and (not isinstance(self, StaffDrawer)) and getattr(self.partition, "print_with_staff_too", 0)):
            alt = symbol[22:]
            ctx_drawText(ctx, x + 5 * self.scale, self.y + 0.8 * self.canvas.default_line_height, alt)
            self._draw_perfect_line(ctx, x, self.y + 16.0 * self.scale, x, self.y)
            self._draw_perfect_line(ctx, x, self.y, x + 60.0 * self.scale, self.y)
      if draw_bars:
        if   start_repeat and end_repeat:
          ctx_drawEllipse(ctx, x -  8.5 * self.scale, y + 0.35 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          ctx_drawEllipse(ctx, x -  8.5 * self.scale, y + 0.65 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          ctx_drawEllipse(ctx, x - 28.5 * self.scale, y + 0.35 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          ctx_drawEllipse(ctx, x - 28.5 * self.scale, y + 0.65 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          self._draw_perfect_rect(ctx, x - 17.8 * self.scale + 0.5, y,      3.0 * self.scale + 0.5,     nheight)
          self._draw_perfect_line(ctx, x - 12.0 * self.scale + 0.5, y, x - 12.0 * self.scale + 0.5, y + nheight)
          self._draw_perfect_line(ctx, x - 20.0 * self.scale + 0.5, y, x - 20.0 * self.scale + 0.5, y + nheight)
          return
        elif start_repeat:
          #ctx_drawEllipse(ctx, x - 7.5 * self.scale, y + 0.35 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          #ctx_drawEllipse(ctx, x - 7.5 * self.scale, y + 0.65 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          #self._draw_perfect_rect(ctx, x - 17.0 * self.scale + 0.5, y,      3.0 * self.scale + 0.5,     nheight)
          #self._draw_perfect_line(ctx, x - 11.0 * self.scale + 0.5, y, x - 11.0 * self.scale + 0.5, y + nheight)
          ctx_drawEllipse(ctx, x - 8.5 * self.scale, y + 0.35 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          ctx_drawEllipse(ctx, x - 8.5 * self.scale, y + 0.65 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          self._draw_perfect_rect(ctx, x - 19.0 * self.scale + 0.5, y,      3.0 * self.scale + 0.5,     nheight)
          self._draw_perfect_line(ctx, x - 12.0 * self.scale + 0.5, y, x - 12.0 * self.scale + 0.5, y + nheight)
          return
        elif end_repeat:
          ctx_drawEllipse(ctx, x - 17.0 * self.scale, y + 0.35 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          ctx_drawEllipse(ctx, x - 17.0 * self.scale, y + 0.65 * height - 1.5 * self.scale, 6.0 * self.scale, 6.0 * self.scale)
          self._draw_perfect_rect(ctx, x - 6.0 * self.scale + 0.5, y,     3.0 * self.scale + 0.5,     nheight)
          self._draw_perfect_line(ctx, x - 9.0 * self.scale + 0.5, y, x - 9.0 * self.scale + 0.5, y + nheight)
          return
        elif start_alternative:
          self._draw_perfect_line(ctx, bar_x - 1, y, bar_x - 1, y + nheight)
          self._draw_perfect_line(ctx, bar_x + 1, y, bar_x + 1, y + nheight)
          return

    if draw_bars:
      if bold: self._draw_perfect_rect(ctx, bar_x - 2, y, 4    ,     nheight)
      else:    self._draw_perfect_line(ctx, bar_x    , y, bar_x, y + nheight)
      
  def draw_strings(self, ctx, x, y, width, height):
    string_x  = x
    string_x2 = x + width
    
    color = "black"
    i = 0
    for string in self.strings:
      string_y = self.string_id_2_y(i)
      i += 1
      if y - 2 < string_y < y + height + 2:
        w = string.width()
        if   w == -1: continue
        elif w ==  8: pass
        else:
          string_color = string.color()
          if string_color != color:
            color = string_color
            ctx.setPen(getattr(qtcore.Qt, color))
          self._draw_perfect_line(ctx, string_x , string_y, string_x2, string_y)
    if color != "black": ctx.setPen(qtcore.Qt.black)
    
  def draw(self, ctx, x, y, width, height, drag = 0, draw_icon = 1, start_y = 15.0):
    if x < self.canvas.start_x:
      width = width + x - self.canvas.start_x
      x = self.canvas.start_x
    if not drag:
      self.start_y = start_y * self.scale + 5 * self.scale
      if self.show_header:
        ctx_drawText(ctx, 3.0 * self.scale, self.y + self.canvas.default_ascent + 2 * self.scale, self.partition.header)
        if (not self.compact) or (not self.need_extra_space_for_strum_dir) or any(note.strum_dir_fx for note in self.partition.notes):
          self.start_y += self.canvas.default_line_height
      if self.compact and not (self.partition is self.canvas.song.partitions[0]): # No need for vertical space for repeat alternative number
        self.start_y -= 10 * self.scale
        
    self.height = int(self.start_y + self.stem_extra_height + self.string_height * len(self.strings) + self.stem_extra_height_bottom + 1)
    
    if Drawer.draw(self, ctx, x, y, width, height, drag):
      ctx.save()
      if not drag:
        if draw_icon: # Draws the partition icon
          draw_bitmap(self.canvas, ctx,
                      description(self.partition.__class__).icon_filename_for(self.partition),
                      4 * self.scale,
                      int(self.y + self.start_y + self.stem_extra_height + (self.height - self.start_y - self.stem_extra_height - self.stem_extra_height_bottom) // 2 - (editor_qt.SMALL_ICON_SIZE * self.scale) // 2),
                      0.5 * self.scale)
          
        self.draw_strings(ctx, x, y, width, height)
        
        ctx.setClipRect(qtcore.QRectF(self.canvas.start_x - 1, 0, self.canvas.width, self.canvas.height), qtcore.Qt.IntersectClip)
        
        bar_y      = self.y + self.start_y + self.stem_extra_height + self.string_height * 0.5
        bar_height = self.string_height * (len(self.strings) - 1)
        for mesure in self.partition.song.mesures:
          if x - 60.0 * self.scale <= self.canvas.time_2_x(mesure.time) <= x + width + 40.0 * self.scale:
            self.draw_mesure(ctx, mesure.time, mesure, bar_y, bar_height)
        if x - 60.0 * self.scale <= self.canvas.time_2_x(mesure.end_time()) <= x + width + 40.0 * self.scale:
          self.draw_mesure(ctx, mesure.end_time(), None, bar_y, bar_height + 1)
          
      time1  = self.canvas.x_2_time(x - self.canvas.start_x)
      time2  = self.canvas.x_2_time(x + width)
      mesure = self.canvas.song.mesure_at(time2)
      if mesure:
        if mesure.rythm2 == 8:
          time1 = (    time1 // 144) * 144
          time2 = (1 + time2 // 144) * 144
        else:
          time1 = (    time1 //  96) *  96
          time2 = (1 + time2 //  96) *  96
          
      notes     = self.partition.notes_at(time1, time2)
      notes_set = set(notes)
      for note in notes:
        while note.linked_from:
          notes_set.add(note.linked_from)
          note = note.linked_from
      notes = list(notes_set)
      notes.sort()
      
      if self.canvas.cursor and (self.canvas.cursor.partition is self.partition):
        if time1 <= self.canvas.cursor <= time2:
          bisect.insort(notes, self.canvas.cursor)
          
      current_time = -1
      previous     = None
      notes_y      = {}
      chords       = []
      if drag and not self.always_draw_stems:
        for note in notes:
          string_id = self.note_string_id(note)
          note_y = notes_y[note] = self.string_id_2_y(string_id)
          #ctx.set_source_rgb(0.0, 0.0, 0.0)
          self.draw_note(ctx, note, string_id, note_y)
          
      else:
        for note in notes:
          if note.duration_fx == "appoggiatura":
            string_id = self.note_string_id(note)
            note_y = notes_y[note] = self.string_id_2_y(string_id)
            self.draw_note(ctx, note, string_id, note_y)
            self.draw_stem_and_beam_for_chord(ctx, [note], { note : note_y }, None, None, 1)
            continue
          
          string_id = self.note_string_id(note)
          note_y = notes_y[note] = self.string_id_2_y(string_id)
          
          if current_time != note.time:
            if (current_time != -1): chords.append(notes_at_time)
            current_time  = note.time
            notes_at_time = []
            
          notes_at_time.append(note)
          
          #ctx.set_source_rgb(0.0, 0.0, 0.0)
          self.draw_note(ctx, note, string_id, note_y)
          
        if current_time != -1: chords.append(notes_at_time)
        
        for i in range(0, len(chords)):
          if   i == 0: previous = None
          elif len(chords[i - 1]) == 1: previous = chords[i - 1][0]
          else:
            min_duration = min([note.duration for note in chords[i - 1]])
            for previous in chords[i - 1]:
              if previous.duration == min_duration: break
          if   i == len(chords) - 1: next = None
          elif len(chords[i + 1]) == 1: next = chords[i + 1][0]
          else:
            min_duration = min([note.duration for note in chords[i + 1]])
            for next in chords[i + 1]:
              if next.duration == min_duration: break
          self.draw_stem_and_beam_for_chord(ctx, chords[i], notes_y, previous, next)
          
          
      ctx.restore()
      
  def draw_stem_and_beam_for_chord(self, ctx, notes, notes_y, previous, next, appo = 0):
    if len(notes) == 1:
      l = notes
    else:
      l = {}
      for note in notes: l[self.note_string_id(note)] = note
      l = [note for (string_id, note) in sorted(l.items())]
      
    x = self.canvas.time_2_x(l[0].time)    
    mesure = self.canvas.song.mesure_at(l[0].time)
    
    if appo:
      y = notes_y[l[ 0]] - self.string_height // 2
      self.draw_stem_and_beam(ctx, x, l[ 0], y - 20 * self.scale, y, mesure, previous, next)
    else:
      self.draw_stem_and_beam(ctx, x, l[ 0], self.y + self.start_y, notes_y[l[ 0]] - self.string_height // 2, mesure, previous, next)
    #ctx.set_source_rgb(0.0, 0.0, 0.0)
    self.draw_strum_direction(ctx, notes)
    
  def draw_strum_direction(self, ctx, notes, offset_x = 0.0):
    if not self.show_header: return
    
    for note in notes:
      if note.strum_dir_fx:
        x = int(self.canvas.time_2_x(note.time) + self.note_offset_x + offset_x)# + 0.5
        if   note.fx == "dead":
          ctx_drawLine(ctx, x                 , self.y + 20 * self.scale, x + 8 * self.scale, self.y + 32 * self.scale)
          ctx_drawLine(ctx, x + 8 * self.scale, self.y + 20 * self.scale, x                 , self.y + 32 * self.scale)
        elif note.strum_dir_fx == "up":
          ctx_drawLine(ctx, x                 , self.y + 20 * self.scale, x + 4 * self.scale, self.y + 32 * self.scale)
          ctx_drawLine(ctx, x + 4 * self.scale, self.y + 32 * self.scale, x + 8 * self.scale, self.y + 20 * self.scale)
        elif note.strum_dir_fx ==  "down":
          ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
          ctx_drawLine(ctx, x                 , self.y + 20 * self.scale, x                 , self.y + 32 * self.scale)
          ctx_drawLine(ctx, x + 8 * self.scale, self.y + 20 * self.scale, x + 8 * self.scale, self.y + 32 * self.scale)
          ctx_drawRect(ctx,  x                 , self.y + 20 * self.scale,     8 * self.scale,           4 * self.scale)
          ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
        elif note.strum_dir_fx ==  "down_thumb":
          ctx_drawLine(ctx, x                 , int(self.y + 32 * self.scale), int(x + 4 * self.scale), int(self.y + 20 * self.scale))
          ctx_drawLine(ctx, int(x + 4 * self.scale), int(self.y + 20 * self.scale), int(x + 8 * self.scale), int(self.y + 32 * self.scale))
        return 1
      
  def note_color(self, note):
    if   note.value < 0:     return qtcore.Qt.gray
    elif note.volume == 255: return qtgui.QColor(217, 0, 0)
    else:
      intensity = int((0.7 - min(0.7, 0.7 * note.volume / 204.0)) * 255)
      return qtgui.QColor(intensity, intensity, intensity)
    
  def draw_note(self, ctx, note, string_id, y, clean_bg = False):
    x  = self.canvas.time_2_x(note.time)
    y += self.note_offset_y
    
    if note.duration_fx == "appoggiatura":
      ctx.setFont(self.canvas.small_font)
      metrics = self.canvas.small_metrics
    else:
      metrics = self.canvas.default_metrics
      
    yy = y + metrics.ascent() / 2 - metrics.descent() / 2
    
    text = self.note_text(note)
    if note.is_dotted(): text += "."
    
    text_size0 = metrics.size(0, text[0])
    text_left  = metrics.leftBearing (text[0])
    text_right = metrics.rightBearing(text[-1])
    
    xx = x + self.note_offset_x  - text_size0.width() / 2 + 0.5
    
    if clean_bg:
      if (not self.drawing_drag_icon) and (note in self.canvas.selections): bg_color = SELECTION_COLOR
      else:                                                                 bg_color = qtcore.Qt.white
      text_size  = metrics.size(0, text)
      ctx.fillRect(int(xx), int(yy - metrics.ascent() + 3), int(text_size.width()), int(text_size.height() - 6), bg_color)
      
    color = self.note_color(note)
    ctx.setPen(color)
    ctx_drawText(ctx, xx, yy, text)
    
    if note.duration_fx == "appoggiatura": ctx.setFont(self.canvas.default_font)
    
    if note.fx     : getattr(self, "draw_note_fx_%s" % note.fx     )(ctx, note, string_id)
    if note.link_fx: getattr(self, "draw_note_fx_%s" % note.link_fx)(ctx, note, string_id)
    ctx.setPen(qtcore.Qt.black)
    
  def draw_note_fx_link(self, ctx, note, string_id):
    if note.linked_from: return
    ax1, ay1, ax2, ay2 = self.note_dimensions(note)
    
    if note.linked_to:
      final_note = note
      lower_y2 = ay2
      while final_note.linked_to:
        final_note = final_note.linked_to
        cx1, cy1, cx2, cy2 = self.note_dimensions(final_note)
        if lower_y2 < cy2: lower_y2 = cy2
      bx1, by1, bx2, by2 = self.note_dimensions(final_note)
      bx1 += self.note_width(note.linked_to)
      lower_y2 = ay2 + (lower_y2 - ay2) * 1.3
    else:
      bx1, by1, bx2, by2 = ax1 + note.duration, ay1, ax2 + note.duration, ay2
      lower_y2 = ay2
      
    ay2 += 4 * self.scale
    by2 += 3 * self.scale
    ctx.save()
    ctx.setPen(BIG_PEN)
    ctx.setBrush(qtcore.Qt.NoBrush)
    path = qtgui.QPainterPath()
    path.moveTo(ax1 + 2, ay2 - self.canvas.default_descent)
    path.cubicTo(
      ax1 +  6 * self.scale, lower_y2 - self.canvas.default_descent + 12 * self.scale,
      bx1 -  6 * self.scale, lower_y2 - self.canvas.default_descent + 12 * self.scale,
      bx1 +  0 * self.scale, by2      - self.canvas.default_descent,
      )
    ctx.drawPath(path)
    ctx.restore()
    
  def draw_note_fx_slide(self, ctx, note, string_id):
    ax1, ay1, ax2, ay2 = self.note_dimensions(note)
    if note.linked_to: bx1, by1, bx2, by2 = self.note_dimensions(note.linked_to)
    else:              bx1, by1, bx2, by2 = ax1 + note.duration, ay1, ax2 + note.duration, ay2
    bx1 -= 3 * self.scale
    x =  bx1 + 2 * self.scale
    y = (by1 + by2) // 2 + self.canvas.default_descent
    ctx.save()
    ctx.setPen(BIG_PEN)
    ctx.setBrush(qtcore.Qt.NoBrush)
    ctx_drawLine(ctx, ax1 + self.note_width(note), (ay1 + ay2) // 2 + self.canvas.default_descent, x, y)
    ctx_drawLine(ctx, x, y, x - 5 * self.scale, y - 5 * self.scale)
    ctx_drawLine(ctx, x, y, x - 5 * self.scale, y + 5 * self.scale)
    ctx.restore()
    
  def draw_note_fx_bend(self, ctx, note, string_id):
    x1, y1, x2, y2 = self.note_dimensions(note)
    x2 -= 3 * self.scale
    x = x1 + 3 * self.scale + self.note_width(note)
    y = (y1 + y2) // 2 + self.canvas.default_descent
    dx = min(x2 - x1, self.canvas.char_h_size * 3)
    xx = x + dx
    yy = y - self.string_height // 2
    ctx.save()
    ctx.setPen(BIG_PEN)
    ctx.setBrush(qtcore.Qt.NoBrush)
    
    path = qtgui.QPainterPath()
    path.moveTo(x, y)
    path.cubicTo(
       x + 12 * self.scale,  y,
       x + dx, yy + 5 * self.scale,
       xx, yy)
    ctx.drawPath(path)
    ctx_drawLine(ctx, xx, yy, xx - 5 * self.scale, yy +     self.scale)
    ctx_drawLine(ctx, xx, yy, xx +     self.scale, yy + 5 * self.scale)
    ctx.setFont(self.canvas.small_font)
    ctx_drawText(ctx, x + dx * 0.1, y1 + (y2 - y1) * 0.2, locale.str(note.bend_pitch))
    ctx.restore()
    
  def draw_note_fx_tremolo(self, ctx, note, string_id):
    x1, y1, x2, ty2 = self.note_dimensions(note)
    tx  = x1 + self.note_width(note) + 3 * self.scale
    ty1 = (y1 + ty2) // 2 - self.scale
    ctx.save()
    ctx.setPen(BIG_PEN)
    ctx.setBrush(qtcore.Qt.NoBrush)
    path = qtgui.QPainterPath()
    path.moveTo(tx, ty1)
    while tx < x2 - 18 * self.scale:
      path.cubicTo(
        tx +  9 * self.scale, ty1 - 8 * self.scale,
        tx +  9 * self.scale, ty1 + 8 * self.scale,
        tx + 18 * self.scale, ty1)
      tx += 18 * self.scale
    ctx.drawPath(path)
    ctx.restore()
    
  def draw_note_fx_dead(self, ctx, note, string_id):
    x1, cy1, x2, cy2 = self.note_dimensions(note)
    cx1 = x1
    cx2 = x1 + self.note_width(note)
    ctx_drawLine(ctx, cx1, cy1, cx2, cy2)
    ctx_drawLine(ctx, cx2, cy1, cx1, cy2)
    
  def draw_note_fx_roll(self, ctx, note, string_id):
    notes = note.chord_notes()
    min_string_id = 99999
    if notes:
      for other in notes:
        other_string_id = self.note_string_id(other)
        if other_string_id >     string_id: return
        if other_string_id < min_string_id: min_string_id = other_string_id
    else:
      min_string_id = self.note_string_id(note) - 1
    x1, y1, x2, y2 = self.note_dimensions(note)
    x = x1 + self.note_width(note)
    y = y2 -(string_id - min_string_id) * self.string_height
    ctx.save()
    ctx.setPen(BIG_PEN)
    ctx.setBrush(qtcore.Qt.NoBrush)
    path = qtgui.QPainterPath()
    path.moveTo(x, y2)
    path.cubicTo(
      x +  7 * self.scale, y2,
      x + 10 * self.scale, y + 15 * self.scale,
      x + 10 * self.scale, y,
      )
    ctx.drawPath(path)
    ctx_drawLine(ctx, x +  5 * self.scale, y + 5 * self.scale,
                 x + 10 * self.scale, y)
    ctx_drawLine(ctx, x + 10 * self.scale, y,
                 x + 15 * self.scale, y + 5 * self.scale)
    ctx.restore()
    
  def draw_note_fx_harmonic(self, ctx, note, string_id): pass
    
  def _nothing(self, ctx, x, y1, y2, note, previous, next): pass
  _round = _nothing

  def _draw_perfect_line_pixel(self, ctx, x1, y1, x2, y2):
    ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
    ctx.drawLine(qtcore.QPoint(int(round(x1)), int(round(y1))), qtcore.QPoint(int(round(x2)), int(round(y2))))
    ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    
  def _draw_perfect_line_pdf(self, ctx, x1, y1, x2, y2):
    ctx.drawLine(qtcore.QPointF(x1, y1), qtcore.QPointF(x2, y2))
    
  def _draw_perfect_rect_pixel(self, ctx, x1, y1, x2, y2):
    ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
    ctx.drawRect(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)))
    ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    
  def _draw_perfect_rect_pdf(self, ctx, x1, y1, x2, y2):
    ctx.drawRect(qtcore.QRectF(x1, y1, x2, y2))
    
  def _white(self, ctx, x, y1, y2, note, previous, next):
    ctx.setPen(WHITE_STEM_COLOR)
    #ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
    #ctx_drawRect(ctx, x, y1, 1, y2 - y1)
    #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    self._draw_perfect_rect(ctx, x, y1, 1, y2 - y1)
    ctx.setPen(qtcore.Qt.black)
  
  def _black(self, ctx, x, y1, y2, note, previous, next):
    ctx.setPen(qtcore.Qt.black)
    self._draw_perfect_line(ctx, x, y2, x, y1)
    
  def _quarter_appo(self, ctx, x, y1, y2, note, previous, next):
    self._quarter8(ctx, x, y1, y2, note, previous, next)
    ctx_drawLine(ctx, x - 4, y1 + 15, x + 8, y1 + 2)
    
  def _quarter(self, ctx, x, y1, y2, note, previous, next, has_previous, has_next, t, dt):
    ctx.setPen(qtcore.Qt.black)
    #ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
    #ctx_drawLine(ctx, x, y2, x, y1)
    self._draw_perfect_line(ctx, x, y2, x, y1)
    
    if has_next:
      if note.time + note.duration < note.time - dt + t:
        self._draw_perfect_rect(ctx, x, y1, note.duration * self.canvas.zoom, 3 * self.scale)
        #ctx_drawRect(ctx, x, y1, note.duration * self.canvas.zoom, 3 * self.scale)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      return
    if has_previous:
      if previous.duration > 72:
        self._draw_perfect_rect(ctx, x, y1, - (note.time - previous.time) * self.canvas.zoom, 3 * self.scale)
        #ctx_drawRect(ctx, x, y1, - (note.time - previous.time) * self.canvas.zoom, 3 * self.scale)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      return
    #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    
    # Single
    ctx.save()
    ctx.translate(x, y1)
    ctx.drawPath(self.canvas.quarter_paths[cmp(y2, y1)])
    ctx.restore()
    
  def _hquarter(self, ctx, x, y1, y2, note, previous, next, has_previous, has_next, t, dt):
    ctx.setPen(qtcore.Qt.black)
    ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
    #ctx_drawLine(ctx, x, y2, x, y1)
    self._draw_perfect_line(ctx, x, y2, x, y1)
    
    sens = cmp(y2, y1)
    if has_next:
      if note.time + note.duration < note.time - dt + t:
        #ctx_drawRect(ctx, x, y1, note.duration * self.canvas.zoom, 3 * self.scale)
        self._draw_perfect_rect(ctx, x, y1, note.duration * self.canvas.zoom, 3 * self.scale)
        if   (next.duration <= 36):
          #ctx_drawRect(ctx, x, y1 + int(5 * sens * self.scale), note.duration * self.canvas.zoom, 3 * self.scale)
          self._draw_perfect_rect(ctx, x, y1 + int(5 * sens * self.scale), note.duration * self.canvas.zoom, 3 * self.scale)
        elif not (has_previous and (previous.duration <= 36)):
          #ctx_drawRect(ctx, x, y1 + int(5 * sens * self.scale), note.duration // 2 * self.canvas.zoom, 3 * self.scale)
          self._draw_perfect_rect(ctx, x, y1 + int(5 * sens * self.scale), note.duration // 2 * self.canvas.zoom, 3 * self.scale)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      return
    if has_previous:
      if (previous.duration > 36): # Else, previous will draw the stem
        #ctx_drawRect(ctx, x, y1 + int(5 * sens * self.scale), - note.duration // 2 * self.canvas.zoom, 3 * self.scale)
        self._draw_perfect_rect(ctx, x, y1 + int(5 * sens * self.scale), - note.duration // 2 * self.canvas.zoom, 3 * self.scale)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      return
    #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    
    # Single
    ctx.save()
    ctx.translate(x, y1)
    ctx.drawPath(self.canvas.quarter_paths[sens])
    ctx.translate(0, 7.0 * sens)
    ctx.drawPath(self.canvas.quarter_paths[sens])
    ctx.restore()
    
  def _hhquarter(self, ctx, x, y1, y2, note, previous, next, has_previous, has_next, t, dt):
    ctx.setPen(qtcore.Qt.black)
    ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
    #ctx_drawLine(ctx, x, y2, x, y1)
    self._draw_perfect_line(ctx, x, y2, x, y1)
    
    sens = cmp(y2, y1)
    dy   = int(5 * sens * self.scale)
    if has_next:
      if note.time + note.duration < note.time - dt + t:
        #ctx_drawRect(ctx, x, y1, note.duration * self.canvas.zoom, 3 * self.scale)
        self._draw_perfect_rect(ctx, x, y1, note.duration * self.canvas.zoom, 3 * self.scale)
        if (next.duration <= 36):
          #ctx_drawRect(ctx, x, y1 + dy, note.duration * self.canvas.zoom, 3 * self.scale)
          self._draw_perfect_rect(ctx, x, y1 + dy, note.duration * self.canvas.zoom, 3 * self.scale)
        elif not (has_previous and (previous.duration <= 36)):
          #ctx_drawRect(ctx, x, y1 + dy, note.duration // 2 * self.canvas.zoom, 3 * self.scale)
          self._draw_perfect_rect(ctx, x, y1 + dy, note.duration // 2 * self.canvas.zoom, 3 * self.scale)
        if (next.duration <= 18):
          #ctx_drawRect(ctx, x, y1 + 2 * dy, note.duration * self.canvas.zoom, 3 * self.scale)
          self._draw_perfect_rect(ctx, x, y1 + 2 * dy, note.duration * self.canvas.zoom, 3 * self.scale)
        elif not (has_previous and (previous.duration <= 18)):
          #ctx_drawRect(ctx, x, y1 + 2 * dy, note.duration // 2 * self.canvas.zoom, 3 * self.scale)
          self._draw_perfect_rect(ctx, x, y1 + 2 * dy, note.duration // 2 * self.canvas.zoom, 3 * self.scale)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      return
    if has_previous:
      if (previous.duration > 36): # Else, previous will draw the stem
        #ctx_drawRect(ctx, x, y1 + dy, - note.duration // 2 * self.canvas.zoom, 3 * self.scale)
        self._draw_perfect_rect(ctx, x, y1 + dy, - note.duration // 2 * self.canvas.zoom, 3 * self.scale)
      if (previous.duration > 18): # Else, previous will draw the stem
        #ctx_drawRect(ctx, x, y1 + 2 * dy, - note.duration // 2 * self.canvas.zoom, 3 * self.scale)
        self._draw_perfect_rect(ctx, x, y1 + 2 * dy, - note.duration // 2 * self.canvas.zoom, 3 * self.scale)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      return
    #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    
    # Single
    ctx.save()
    ctx.translate(x, y1)
    ctx.drawPath(self.canvas.quarter_paths[sens])
    ctx.translate(0, 7.0 * sens)
    ctx.drawPath(self.canvas.quarter_paths[sens])
    ctx.translate(0, 7.0 * sens)
    ctx.drawPath(self.canvas.quarter_paths[sens])
    ctx.restore()

  def _quarter4(self, ctx, x, y1, y2, note, previous, next):
    dt           = note.time % 96
    has_next     = next     and (next.time + next.duration <= note.time - dt + 96) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.time >= note.time - dt) and (previous.time + previous.duration >= note.time)
    self._quarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 96, dt)
    
  def _quarter8(self, ctx, x, y1, y2, note, previous, next):
    dt           = note.time % 144
    has_next     = next     and (next    .duration <= 48 * 1.5) and (next.time + next.duration <= note.time - dt + 144) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.duration <= 48 * 1.5) and (previous.time >= note.time - dt) and (previous.time + previous.duration == note.time)
    self._quarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 144, dt)
    
  def _hquarter4(self, ctx, x, y1, y2, note, previous, next):
    dt           = note.time % 96
    has_next     = next     and (next.time + next.duration <= note.time - dt + 96) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.time >= note.time - dt) and (previous.time + previous.duration == note.time)
    self._hquarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 96, dt)
    
  def _hquarter8(self, ctx, x, y1, y2, note, previous, next):
    dt           = note.time % 144
    has_next     = next     and (next    .duration <= 48 * 1.5) and (next.time + next.duration <= note.time - dt + 144) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.duration <= 48 * 1.5) and (previous.time >= note.time - dt) and (previous.time + previous.duration == note.time)
    self._hquarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 144, dt)
    
  def _hhquarter4(self, ctx, x, y1, y2, note, previous, next):
    dt           = note.time % 96
    has_next     = next     and (next.time + next.duration <= note.time - dt + 96) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.time >= note.time - dt) and (previous.time + previous.duration == note.time)
    self._hhquarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 96, dt)
    
  def _hhquarter8(self, ctx, x, y1, y2, note, previous, next):
    dt           = note.time % 144
    has_next     = next     and (next    .duration <= 48 * 1.5) and (next.time + next.duration <= note.time - dt + 144) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.duration <= 48 * 1.5) and (previous.time >= note.time - dt) and (previous.time + previous.duration == note.time)
    self._hhquarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 144, dt)
       
  def _black_triplet(self, ctx, x, y1, y2, note, previous, next):
    sens = cmp(y2, y1)
    ctx.setPen(qtcore.Qt.black)
    #ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
    #ctx_drawLine(ctx, x, y2, x, y1 + 3 * sens)
    self._draw_perfect_line(ctx, x, y2, x, y1 + 3 * sens)
    
    if note.time % 192 == 64:
      ctx_drawLine(ctx, x - 64 * self.canvas.zoom, y1, x + 64 * self.canvas.zoom, y1)
      ctx.setFont(self.canvas.small_font)
      if    y2 > y1: ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 - self.canvas.small_metrics.descent(), "3")
      else:          ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 + self.canvas.small_metrics.ascent (), "3")
      ctx.setFont(self.canvas.default_font)
      
   # ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    
  def _quarter_triplet(self, ctx, x, y1, y2, note, previous, next):
    dt           = note.time % 96
    has_next     = next     and (next.time + next.duration <= note.time - dt + 96) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.time >= note.time - dt) and (previous.time + previous.duration >= note.time)
    self._quarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 96, dt)
    
    if dt == 32:
      ctx.setFont(self.canvas.small_font)
      if    y2 > y1: ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 - self.canvas.small_metrics.descent(), "3")
      else:          ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 + self.canvas.small_metrics.ascent (), "3")
      ctx.setFont(self.canvas.default_font)
    
  def _hquarter_triplet(self, ctx, x, y1, y2, note, previous, next):
    dt   = note.time % 96
    has_next     = next     and (next.time + next.duration <= note.time - dt + 96) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.time >= note.time - dt) and (previous.time + previous.duration == note.time)
    self._hquarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 96, dt)
    
    if (note.time % 48) == 16:
      ctx.setFont(self.canvas.small_font)
      if    y2 > y1: ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 - self.canvas.small_metrics.descent(), "3")
      else:          ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 + self.canvas.small_metrics.ascent (), "3")
      ctx.setFont(self.canvas.default_font)
      
  def _hhquarter_triplet(self, ctx, x, y1, y2, note, previous, next):
    dt   = note.time % 96
    has_next     = next     and (next.time + next.duration <= note.time - dt + 96) and (note.time + note.duration == next.time)
    has_previous = previous and (previous.time >= note.time - dt) and (previous.time + previous.duration == note.time)
    self._hhquarter(ctx, x, y1, y2, note, previous, next, has_previous, has_next, 96, dt)
    
    if (note.time % 24) == 8:
      ctx.setFont(self.canvas.small_font)
      if    y2 > y1: ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 - self.canvas.small_metrics.descent(), "3")
      else:          ctx_drawText(ctx, x - self.canvas.char_h_size // 2, y1 + self.canvas.small_metrics.ascent (), "3")
      ctx.setFont(self.canvas.default_font)
      
  _drawers = { # Maps durations to the corresponding drawer function
    576 : _round, # Dotted
    288 : _white,
    144 : _black,
    72  : _quarter4,
    36  : _hquarter4,
    18  : _hhquarter4,

    384 : _round, # Non-dotted
    192 : _white,
    96  : _black,
    48  : _quarter4,
    24  : _hquarter4,
    12  : _hhquarter4,

    64  : _black_triplet,
    32  : _quarter_triplet,
    16  : _hquarter_triplet,
    8   : _hhquarter_triplet,
    }
  _drawers8 = { # Maps durations to the corresponding drawer function for x/8 rythms
    576 : _round, # Dotted
    288 : _white,
    144 : _black,
    72  : _quarter8,
    36  : _hquarter8,
    18  : _hhquarter8,
    
    384 : _round, # Non-dotted
    192 : _white,
    96  : _black,
    48  : _quarter8,
    24  : _hquarter8,
    12  : _hhquarter8,
    
    # Does triplets make sense in 6/8 rythms ???
    64  : _black_triplet,
    32  : _quarter_triplet,
    16  : _hquarter_triplet,
    8   : _hhquarter_triplet,
    }
  
  def draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure = None, previous = None, next = None):
    x =     x + self.note_offset_x
    if   note.duration_fx == "appoggiatura": return self._quarter_appo(ctx, x, y1, y2, note, previous, next)
    elif note.duration_fx == "fermata":      self.draw_fermata(ctx, x)
    elif note.duration_fx == "breath":       self.draw_breath (ctx, x)
    if mesure and (mesure.rythm2 == 8):       return (self._drawers8.get(note.duration) or PartitionDrawer._nothing)(self, ctx, x, y1, y2, note, previous, next)
    else:                                     return (self._drawers .get(note.duration) or PartitionDrawer._nothing)(self, ctx, x, y1, y2, note, previous, next)

  def draw_fermata(self, ctx, x):
    ctx.save() # When draw_fermata, the current color is the one for the stem !
    ctx.setPen(qtcore.Qt.black)
    ctx.setBrush(qtcore.Qt.black)
    ctx_drawEllipse(ctx, x - 2.0 * self.scale, self.y + 18.0 * self.scale, 4.0 * self.scale, 4.0 * self.scale)
    
    path = qtgui.QPainterPath()
    path.moveTo(x + 10.0 * self.scale, self.y + 20.0 * self.scale)
    path.arcTo(x - 10.0 * self.scale, self.y + 10.0 * self.scale,
               20.0 * self.scale, 20.0 * self.scale,
               0.0, 180.0
    )
    path.arcTo(x + 10.0 * self.scale, self.y + 9.0 * self.scale,
               -20.0 * self.scale, 21.0 * self.scale,
               0.0, 180.0
    )
    ctx.drawPath(path)
    ctx.restore() # Restore color
    
  def draw_breath(self, ctx, x):
    draw_bitmap(self.canvas, ctx, os.path.join(globdef.DATADIR, "effet_breath.png"), x, self.y + 7.0 * self.scale, 0.18 * self.scale)
    
    
    
class TablatureDrawer(PartitionDrawer):
  def __init__(self, canvas, partition, compact = False):
    PartitionDrawer.__init__(self, canvas, partition, compact)
    self.height = 300
    self.strings = partition.view.strings
    self.string_height = canvas.default_line_height + 1 * self.scale
    self.stem_extra_height = self.string_height
    self.stem_extra_height_bottom = self.string_height * 0.6
    self.note_offset_x = 8.0 * self.scale
    self.drawing_drag_icon = 0
    
  def create_cursor(self, time, duration, string_id, value):
    cursor = PartitionDrawer.create_cursor(self, time, duration, string_id, value)
    cursor.string_id = string_id
    return cursor
  
  def partition_listener(self, partition, type, new, old):
    if type is object:
      if new.get("capo", 0) != old.get("capo", 0):
        self.canvas.render_all()
        
    PartitionDrawer.partition_listener(self, partition, type, new, old)
    
  def mouse_motion_note(self, value, delta): return value + abs(delta)
  
  def note_string_id(self, note): return self.partition.view.note_string_id(note)
  
  def note_text(self, note):
    if note.fx == "harmonic":
      if note is self.canvas.cursor: return "_♢"
      return self.strings[self.note_string_id(note)].value_2_text(note) + "♢"
    if note is self.canvas.cursor: return "_"
    return self.strings[self.note_string_id(note)].value_2_text(note)
  
  def note_width(self, note):
    return self.canvas.char_h_size * len(self.note_text(note)) + 6 * self.scale
  
  def draw(self, ctx, x, y, width, height, drag = 0, draw_icon = 1, start_y = 15):
    self.drawing_drag_icon = drag
    return PartitionDrawer.draw(self, ctx, x, y, width, height, drag, draw_icon, start_y)
    
  def draw_note(self, ctx, note, string_id, y):
    if note.value >= 0: PartitionDrawer.draw_note(self, ctx, note, string_id, y, clean_bg = True)
    else:               PartitionDrawer.draw_note(self, ctx, note, string_id, y, clean_bg = False)
    
  def draw_note_fx_link(self, ctx, note, string_id):
    ax1, ay1, ax2, ay2 = self.note_dimensions(note)
    if note.linked_to: bx1, by1, bx2, by2 = self.note_dimensions(note.linked_to)
    else:              bx1, by1, bx2, by2 = ax1 + note.duration, ay1, ax2 + note.duration, ay2
    anb_char = len(self.note_text(note))
    ctx.save()
    ctx.setPen(BIG_PEN)
    ctx.setBrush(qtcore.Qt.NoBrush)
    path = qtgui.QPainterPath()
    path.moveTo(ax1 + 5 + self.canvas.char_h_size * anb_char, (ay1 + ay2) // 2 + self.canvas.default_descent)
    path.cubicTo(
      ax1 + 8 + self.canvas.char_h_size * anb_char, (ay1 + ay2) // 2 + self.canvas.default_descent + 4,
      bx1 - 1                                     , (by1 + by2) // 2 + self.canvas.default_descent + 4,
      bx1 + 2                                     , (by1 + by2) // 2 + self.canvas.default_descent)
    ctx.drawPath(path)
    if note.linked_to:
      if   note.value < note.linked_to.value:
        ctx_drawText(ctx, (ax1 + self.canvas.char_h_size * anb_char + bx1) // 2, (ay1 + ay2 + by1 + by2) // 4 + self.canvas.default_descent // 2, "h")
      elif note.value > note.linked_to.value:
        ctx_drawText(ctx, (ax1 + self.canvas.char_h_size * anb_char + bx1) // 2, (ay1 + ay2 + by1 + by2) // 4 + self.canvas.default_descent // 2, "p")
    ctx.restore()
    
  def draw_strum_direction(self, ctx, notes, offset_x = 0.0):
    return PartitionDrawer.draw_strum_direction(self, ctx, notes, -4.0 * self.scale)

  
class DrumsDrawer(PartitionDrawer):
  def __init__(self, canvas, partition, compact = False):
    PartitionDrawer.__init__(self, canvas, partition, compact)
    self.height = 300
    self.strings = partition.view.strings
    self.string_height = canvas.default_line_height + 2 * self.scale
    self.stem_extra_height = self.string_height
    
  def mouse_motion_note(self, value, delta): return value
  
  def note_string_id(self, note):
    return self.partition.view.note_string_id(note)
    
  def note_text(self, note):
    if note is self.canvas.cursor: return "_"
    return "O"
  
  def on_touchscreen_new_note(self, event):
    PartitionDrawer.on_touchscreen_new_note(self, event)
    return 0 # No change note by dragging up or down
  
  def draw(self, ctx, x, y, width, height, drag = 0):
    PartitionDrawer.draw(self, ctx, x, y, width, height, drag)
    if not drag:
      ctx.set_source_rgb(0.4, 0.4, 0.4)
      ctx.set_font_size(self.canvas.default_font_size * 0.8)
      for i in range(len(self.strings)):
        ctx.move_to(self.canvas.start_x + 3, self.string_id_2_y(i))
        ctx.show_text(model.DRUM_PATCHES[self.strings[i].base_note])
        
      ctx.set_source_rgb(0.0, 0.0, 0.0)
      ctx.set_font_size(self.canvas.default_font_size)
      
  def draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure = None, previous_time = -32000, next_time = 32000):
    x = x + self.string_height // 2.5
    PartitionDrawer.draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure, previous_time, next_time)


STAFF_STRING_PREVIOUS = { 0 : -1, 2 : 0, 4 : 2, 5 : 4, 7 : 5, 9 :  7, 11 :  9 }
STAFF_STRING_NEXT     = { 0 :  2, 2 : 4, 4 : 5, 5 : 7, 7 : 9, 9 : 11, 11 : 12 }

class StaffDrawer(PartitionDrawer):
  def __init__(self, canvas, partition, compact = False):
    PartitionDrawer.__init__(self, canvas, partition, compact)
    if compact:
      self.string_height     = canvas.default_line_height / 3.5
      self.stem_extra_height = 12 * self.scale + self.string_height
    else:
      self.string_height     = canvas.default_line_height / 2.5
      self.stem_extra_height = 15 * self.scale + self.string_height
      
    self.stem_extra_height_bottom =  3 * self.scale + self.string_height
    self.height         = 300
    self.strings        = []
    self.value_2_string = {}
    string_values_and_line_styles = []
    
    g_key = getattr(self.partition, "g_key", 1)
    f_key = getattr(self.partition, "f_key", 0)
    if g_key or (not f_key):
      string_values_and_line_styles += [(79, 0, 0), (77, 2, 0), (76, 0, 0), (74, 2, 0), (72, 0, 0), (71, 2, 0), (69, 0, 0), (67, 2, 0), (65, 0, 0), (64, 2, 0), (62, 0, 0)]
      if f_key: string_values_and_line_styles += [(60, 1, 1)]
    if f_key:
      string_values_and_line_styles += [(59, 0, 0), (57, 2, 0), (55, 0, 0), (53, 2, 0), (52, 0, 0), (50, 2, 0), (48, 0, 0), (47, 2, 0), (45, 0, 0), (43, 2, 0), (41, 0, 0)]
      
    if getattr(partition, "g8", 0):
      string_values_and_line_styles = [(v - 12, d, p) for (v, d, p) in string_values_and_line_styles]
      
    alterations = model.TONALITIES[partition.tonality]
    if alterations:
      if alterations[0] == model.DIESES[0]: self.alteration_type =  1 # diese
      else:                                 self.alteration_type = -1 # bemol
    else:                                   self.alteration_type =  0
    self.alterations  = set(alterations)
    alterations2      = set(alterations)
    
    for note_value, line_style, pos in string_values_and_line_styles:
      alteration      = 0
      draw_alteration = 0
      if (note_value % 12) in self.alterations:
        alteration = self.alteration_type
        if (note_value % 12) in alterations2:
          alterations2.remove(note_value % 12)
          draw_alteration = 1
      StaffString(self, note_value, line_style, alteration, draw_alteration, pos)
    self._sort_strings()
    
  def create_cursor(self, time, duration, string_id, value):
    return PartitionDrawer.create_cursor(self, time, duration, string_id, value - self.strings[string_id].alteration)
  
  def mouse_motion_note(self, value, delta):
    v = value + delta
    unaltered_value, alteration = model.TONALITY_NOTES[self.partition.tonality][v % 12]
    string = self.get_string(v - alteration)
    return string.base_note + string.alteration
  
  def get_orig_string(self, value):
    if getattr(self.partition, "g8", 0): value -= 12
    return self.value_2_string[value + offset]
    
  def get_orig_string_by_pos(self, pos, key = ""):
    if not key:
      if   self.partition.g_key: key = "g"
      elif self.partition.f_key: key = "f"
      else:                      key = "g"
    if   key == "g": value = (77, 74, 71, 67, 64)[pos]
    elif key == "f": value = (57, 53, 50, 47, 43)[pos]
    if getattr(self.partition, "g8", 0): value -= 12
    return self.value_2_string[value]
    
  def partition_listener(self, partition, type, new, old):
    if (old["g_key"] != new["g_key"]) or (old["f_key"] != new["f_key"]): # Key changed
      self.__init__(self.canvas, self.partition, self.compact)
      self.canvas.render_all()
      
    PartitionDrawer.partition_listener(self, partition, type, new, old)
    
  def draw_strings(self, ctx, x, y, width, height):
    if getattr(self.partition, "g8", 0): offset = -12
    else:                                offset =  0
    scale = self.string_height * 2.5 / 14.6666666667
    
    if self.partition.g_key:
      key_y = int(self.string_id_2_y(self.get_orig_string_by_pos(3).id) - 120.0 * scale * 0.4)
      draw_bitmap(self.canvas, ctx, os.path.join(globdef.DATADIR, "clef_de_sol.png"), 2, key_y, scale * 0.4)
      if self.partition.g8:
        ctx_drawText(ctx, 26.0 * self.scale, key_y, "8")
        
    if self.partition.f_key:
      draw_bitmap(self.canvas, ctx,
                  os.path.join(globdef.DATADIR, "clef_de_fa.png"),
                  2,
                  int(self.string_id_2_y(self.get_orig_string_by_pos(1, "f").id) - 29.0 * scale * .4),
                  scale * 0.4)
      
    PartitionDrawer.draw_strings(self, ctx, 0, y, width + x, height)
    
  def draw(self, ctx, x, y, width, height, drag = 0):
    PartitionDrawer.draw(self, ctx, x, y, width, height, drag, 0)
    if not drag:
      if len(self.canvas.song.mesures) > 1: mesure = self.canvas.song.mesures[1]
      else:                                 mesure = self.canvas.song.mesures[0]
      t = str(mesure.rythm1)
      if self.compact:
        ctx.setFont(self.canvas.rhythm_small_font)
        if len(t) == 1:
          ctx_drawText(ctx, self.canvas.start_x - self.scale * 18.0, self.string_id_2_y(self.get_orig_string_by_pos(2).id) - 1.0 * self.scale, t)
        else:
          ctx_drawText(ctx, self.canvas.start_x - self.scale * 24.0, self.string_id_2_y(self.get_orig_string_by_pos(2).id) - 1.0 * self.scale, t)
        ctx_drawText(ctx, self.canvas.start_x - self.scale * 18.0, self.string_id_2_y(self.get_orig_string_by_pos(4).id) - 1.0 * self.scale, str(mesure.rythm2))
        
      else:
        if len(t) == 1:
          ctx.setFont(self.canvas.rhythm_font)
          ctx_drawText(ctx, self.canvas.start_x - self.scale * 25.0, self.string_id_2_y(self.get_orig_string_by_pos(2).id), t)
        else:
          ctx.setFont(self.canvas.rhythm_small_font)
          ctx_drawText(ctx, self.canvas.start_x - self.scale * 28.0, self.string_id_2_y(self.get_orig_string_by_pos(2).id) - self.string_height / 2, t)
          ctx.setFont(self.canvas.rhythm_font)
        ctx_drawText(ctx, self.canvas.start_x - self.scale * 25.0, self.string_id_2_y(self.get_orig_string_by_pos(4).id), str(mesure.rythm2))
      
      ctx.setFont(self.canvas.rhythm_small_font)
      nb_alteration = sum(1 for string in self.strings if string.draw_alteration)
      if self.compact:
        x = self.canvas.start_x * (0.46 - 0.03 * nb_alteration)
      else:
        x = self.canvas.start_x * (0.53 - 0.03 * nb_alteration)
      y = self.y + self.start_y + self.stem_extra_height + self.string_height * 0.38
      for string in self.strings:
        y += self.string_height
        if string.draw_alteration:
          if string.alteration == -1:
            ctx_drawText(ctx, x + self.canvas.char_h_size * 0.55 * model.BEMOLS.index(string.base_note % 12), y - 1.4 * self.scale, "♭")
          else:
            ctx_drawText(ctx, x + self.canvas.char_h_size * 0.55 * model.DIESES.index(string.base_note % 12), y + 2.5 * self.scale, "♯")
            
      ctx.setFont(self.canvas.default_font)
      
      if self.compact:
        #ctx.save()
        #ctx.setClipRect(x, 0, self.canvas.width, self.canvas.height, qtcore.Qt.IntersectClip)
        self.draw_pauses(ctx, x + self.canvas.start_x, width)
        #ctx.restore()
        
  def _sort_strings(self):
    self.strings.sort(key = lambda n: -n.base_note)
    for i, string in enumerate(self.strings): string.id = i
    self.mesure_ys = []
    
  def get_string(self, note_value, create = 1):
    if note_value > self.strings[0].base_note:
      if create:
        new_string_value = STAFF_STRING_NEXT[self.strings[0].base_note % 12] + (self.strings[0].base_note // 12) * 12
        if self.strings[0].line_style == 0: new_string_line_style = 1
        else:                               new_string_line_style = 0
        if (new_string_value % 12) in self.alterations: alteration = self.alteration_type
        else:                                           alteration = 0
        string = StaffString(self, new_string_value, new_string_line_style, alteration, 0, -1)
        self._sort_strings()
        self.canvas.render_all()
        return self.get_string(note_value, create)
      else:
        return None
      
    string = self.value_2_string.get(note_value)
    if string: return string
    
    if create:
      new_string_value = STAFF_STRING_PREVIOUS[self.strings[-1].base_note % 12] + (self.strings[-1].base_note // 12) * 12
      if self.strings[-1].line_style == 0: new_string_line_style = 1
      else:                                new_string_line_style = 0
      if (new_string_value % 12) in self.alterations: alteration = self.alteration_type
      else:                                           alteration = 0
      string = StaffString(self, new_string_value, new_string_line_style, alteration, 0, 1)
      self._sort_strings()
      self.canvas.render_all()
      return self.get_string(note_value, create)
    
  def note_string_id(self, note):
    unaltered_value, alteration = note.unaltered_value_and_alteration()
    return self.get_string(unaltered_value, 1).id
  
  def note_text(self, note):
    if note is self.canvas.cursor: return "-"
    return self.get_string(note.unaltered_value_and_alteration()[0]).value_2_text(note)
  
  def note_dimensions(self, note):
    string_id = self.note_string_id(note)
    x = self.canvas.time_2_x(note.time)
    y = self.string_id_2_y(string_id) - self.string_height
    return (x, y,
      x + max(note.duration * self.canvas.zoom, self.string_height * 2.5),
      y + self.string_height * 2 )
  
  def note_width(self, note):
    if note.duration_fx == "appoggiatura": return 1.4 * self.string_height
    return 2.5 * self.string_height
  
  def note_previous(self, note):
    string_id = self.note_string_id(note)
    while 1:
      note = note.previous()
      if not note: return None
      if self.note_string_id(note) == string_id: return note
      
  def render_note(self, note):
    mesure = self.canvas.song.mesure_at(note)
    if mesure.rythm2 == 8: time1 = (note.link_start() // 144) * 144; time2 = max(note.link_end(), time1 + 144)
    else:                  time1 = (note.link_start() //  96) *  96; time2 = max(note.link_end(), time1 +  96)
    
    if self.partition.notes: # Required for updating sharp / natural / flat symbol correctly
      time2 = max(time2, self.partition.notes[-1].end_time())
      
    extra_width = 15.0 * self.scale # for # and b
    self.canvas.render_pixel(
      self.canvas.time_2_x(time1) - extra_width,
      self.y,
      (time2 - time1) * self.canvas.zoom + 10 * self.scale + extra_width,
      self.height,
      )
    
  def calc_mesure_ys(self):
    self.mesure_ys = []
    if self.partition.g_key:
      y1 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(0, "g")))
      y2 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(4, "g")))
      self.mesure_ys.append((y1 - self.y, y2 - y1))
    if self.partition.f_key:
      y1 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(0, "f")))
      y2 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(4, "f")))
      self.mesure_ys.append((y1 - self.y, y2 - y1))
      
  def draw_mesure(self, ctx, time, mesure, y, height):
    if not self.mesure_ys:
      if self.partition.g_key:
        y1 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(0, "g")))
        y2 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(4, "g")))
        self.mesure_ys.append((y1 - self.y, y2 - y1))
      if self.partition.f_key:
        y1 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(0, "f")))
        y2 = self.string_id_2_y(self.strings.index(self.get_orig_string_by_pos(4, "f")))
        self.mesure_ys.append((y1 - self.y, y2 - y1))
        
    for y, height in self.mesure_ys:
      PartitionDrawer.draw_mesure(self, ctx, time, mesure, self.y + y, height)
      
  def draw_note(self, ctx, note, string_id, y):
    x      = self.canvas.time_2_x(note.time)
    string = self.strings[string_id]
    color  = self.note_color(note)
    
    ctx.save()
    ctx.setPen(color)
    ctx.setBrush(color)
    if   note.fx == "harmonic":
      ctx.drawPolygon(
        qtcore.QPointF(x + 0.3 * self.string_height, y),
        qtcore.QPointF(x + 1.3 * self.string_height, y + self.string_height),
        qtcore.QPointF(x + 2.3 * self.string_height, y),
        qtcore.QPointF(x + 1.3 * self.string_height, y - self.string_height),
      )
      if note.base_duration() in (192, 384):
        ctx.setBrush(qtcore.Qt.white)
        ctx.drawPolygon(
          qtcore.QPointF(x + 0.6 * self.string_height, y),
          qtcore.QPointF(x + 1.3 * self.string_height, y + 0.7 * self.string_height),
          qtcore.QPointF(x + 2.0 * self.string_height, y),
          qtcore.QPointF(x + 1.3 * self.string_height, y - 0.7 * self.string_height),
        )
      
    elif note.fx != "dead":
      ctx.translate(x + 1.2 * self.string_height, y + 0.5)
      ctx.rotate(-25.0)
      
      if note.duration_fx == "appoggiatura":
        # White appoggiatura should never exist !
        ctx_drawEllipse(ctx,
          -0.5 * self.string_height,
          -0.4 * self.string_height,
           1.2 * self.string_height,
           0.8 * self.string_height,
        )
      else:
        ctx_drawEllipse(ctx,
          -1.125 * self.string_height,
          -0.825 * self.string_height,
           2.25  * self.string_height,
           1.65  * self.string_height,
        )
        if note.base_duration() in (192, 384): # White notes:
          ctx.setBrush(qtcore.Qt.white)
          ctx.rotate(-10)
          ctx_drawEllipse(ctx,
            -1.1    * self.string_height,
            -0.55   * self.string_height,
             2.05   * self.string_height,
             1.0    * self.string_height,
          )
          
    ctx.restore()
    
    if string.pos != 0:
      i = string_id
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
      while self.strings[i].pos != 0:
        if self.strings[i].line_style > 0:
          line_y = self.string_id_2_y(i)
          #ctx_drawLine(ctx, x - 3, line_y, x + 19.0 * self.scale, line_y)
          self._draw_perfect_line(ctx, x - 0.5 * self.string_height, line_y, x + 3.0 * self.string_height, line_y)
        i -= string.pos
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
    elif (note.base_duration() in (192, 384)) and (string.line_style == 2):
      line_y = self.string_id_2_y(string_id)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
      #ctx_drawLine(ctx, x, line_y, x + 17.0 * self.scale, line_y)
      #ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      self._draw_perfect_line(ctx, x, line_y, x + 17.0 * self.scale, line_y)
      
    alteration = abs(note.value) - string.base_note
    
    previous = self.note_previous(note)
    if previous:
      previous_alteration = abs(previous.value) - string.base_note
      if self.partition.song.mesure_at(previous) is not self.partition.song.mesure_at(note):
        if previous_alteration != string.alteration:
          previous_alteration = -99 # force the drawing of the alteration mark
    else: previous_alteration = string.alteration

    if alteration != previous_alteration:
      if   alteration == -2: t = "♭♭"
      elif alteration == -1: t = "♭"
      elif alteration ==  0: t = "♮"
      elif alteration ==  1: t = "♯"
      elif alteration ==  2: t = "♯♯"
      else:                  t = "?"
      ctx_drawText(ctx, x - self.canvas.char_h_size * 0.8, y + self.canvas.default_ascent // 2 - 1, t)
      
    if note.is_dotted():
      if string.line_style == 0: ctx_drawEllipse(ctx, x + 3.5 * self.string_height, y - 0.2 * self.string_height, 3 * self.scale, 3 * self.scale)
      else:                      ctx_drawEllipse(ctx, x + 3.5 * self.string_height, y - 1   * self.string_height, 3 * self.scale, 3 * self.scale)
      
    if note.fx     : getattr(self, "draw_note_fx_%s" % note.fx     )(ctx, note, string_id)
    if note.link_fx: getattr(self, "draw_note_fx_%s" % note.link_fx)(ctx, note, string_id)
    
  def draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure = None, previous_time = -32000, next_time = 32000):
    #if note.duration_fx == "appoggiatura": x  += int(2.05 * self.string_height)
    #else:                                  x  += int(2.325 * self.string_height)
    if note.duration_fx == "appoggiatura": x  += 1.77 * self.string_height
    else:                                  x  += 2.27 * self.string_height
    if note.duration_fx == "fermata": self.draw_fermata(ctx, x)
    y2 += self.string_height // 2
    PartitionDrawer.draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure, previous_time, next_time)
    
  _drawers = PartitionDrawer._drawers.copy()
  _drawers[288] = _drawers[192] = PartitionDrawer._black
  _drawers8 = PartitionDrawer._drawers8.copy()
  _drawers8[288] = _drawers8[192] = PartitionDrawer._black
  
  def draw_strum_direction(self, ctx, notes, offset_x = 0.0):
    return PartitionDrawer.draw_strum_direction(self, ctx, notes, 4.0 * self.scale)
  
  def draw_pauses(self, ctx, x, width):
    t1 = max(0, self.canvas.x_2_time(x))
    if self.partition.notes and (self.partition.notes[ 0].time       > t1): t1 = self.partition.notes[ 0].time
    t2 = max(0, self.canvas.x_2_time(x + width))
    if self.partition.notes and (self.partition.notes[-1].end_time() < t2): t2 = self.partition.notes[-1].end_time()
    
    import bisect
    mesure_id = bisect.bisect_right(self.partition.song.mesures, t1) - 1
    mesure = self.partition.song.mesures[mesure_id]
    if mesure_id == 0: t = max(mesure.time, t1) # Anachrousis
    else:              t = mesure.time
    
    bitmap_scale = self.string_height / 30.0
    
    def advance_t(old_t, t):
      new_t = t
      for note2 in self.partition.notes_at(old_t, t):
        if new_t < note2.end_time(): new_t = note2.end_time()
      if new_t != t:
        return advance_t(t, new_t)
      return new_t
    
    
    def draw_pause(mesure, t1, t2):
      if t1 == t2: return
      t = t1 - mesure.time
      if t % 96 == 0:
        if t2 >= t1 + 384:
          ctx_drawRect(ctx, self.canvas.time_2_x((t1 + t2) // 2) - 10, self.string_id_2_y(self.get_orig_string_by_pos(1).id), 20, 5)
          if (t1 == mesure.time) and (t2 == mesure.end_time()): return
          return draw_pause(mesure, t1 + 384, t2)
        
        if t2 >= t1 + 192:
          ctx_drawRect(ctx, self.canvas.time_2_x((t1 + t2) // 2) - 9, self.string_id_2_y(self.get_orig_string_by_pos(2).id) - 5, 18, 5)
          return draw_pause(mesure, t1 + 192, t2)
        
      if t2 >= t1 + 144:
        x = self.canvas.time_2_x(t1) + 2
        y = self.string_id_2_y(self.get_orig_string_by_pos(0).id) + self.string_height
        draw_bitmap(self.canvas, ctx, os.path.join(globdef.DATADIR, "rest_96.png"), x, y, bitmap_scale)
        #ctx.arc(x + 15, y + 20, 2.0, 0, 2.0 * math.pi)
        #ctx.fill()
        ctx_drawEllipse(ctx, x + 14.0 * self.scale, y + 19.0 * self.scale, 3.0 * self.scale, 3.0 * self.scale)
        return draw_pause(mesure, t1 + 144, t2)
      
      if t2 >= t1 + 96:
        draw_bitmap(self.canvas, ctx,
                    os.path.join(globdef.DATADIR, "rest_96.png"),
                    self.canvas.time_2_x(t1) + 2,
                    self.string_id_2_y(self.get_orig_string_by_pos(0).id) + self.string_height,
                    bitmap_scale)
        return draw_pause(mesure, t1 + 96, t2)
      
      if t2 >= t1 + 72:
        x = self.canvas.time_2_x(t1) + 2
        y = self.string_id_2_y(self.get_orig_string_by_pos(0).id) + 2.5 * self.string_height
        draw_bitmap(self.canvas, ctx, os.path.join(globdef.DATADIR, "rest_48.png"), x, y, bitmap_scale)
        #ctx.arc(x + 13, y + 16, 1.5, 0, 2.0 * math.pi)
        #ctx.fill()
        ctx_drawEllipse(ctx, x + 12.25 * self.scale, y + 15.25 * self.scale, 2.5 * self.scale, 2.5 * self.scale)
        return draw_pause(mesure, t1 + 72, t2)

      if t2 >= t1 + 48:
        draw_bitmap(self.canvas, ctx,
                    os.path.join(globdef.DATADIR, "rest_48.png"),
                    self.canvas.time_2_x(t1) + 2,
                    self.string_id_2_y(self.get_orig_string_by_pos(0).id) + 2.5 * self.string_height,
                    bitmap_scale)
        return draw_pause(mesure, t1 + 48, t2)

      if t2 >= t1 + 36:
        x = self.canvas.time_2_x(t1) + 2
        y = self.string_id_2_y(self.get_orig_string_by_pos(0).id) + 2.5 * self.string_height
        draw_bitmap(self.canvas, ctx, os.path.join(globdef.DATADIR, "rest_24.png"), x, y, bitmap_scale)
        #ctx.arc(x + 11, y + 16, 1.5, 0, 2.0 * math.pi)
        #ctx.fill()
        ctx_drawEllipse(ctx, x + 10.25 * self.scale, y + 15.25 * self.scale, 2.5 * self.scale, 2.5 * self.scale)
        return draw_pause(mesure, t1 + 36, t2)

      if t2 >= t1 + 24:
        draw_bitmap(self.canvas, ctx,
                    os.path.join(globdef.DATADIR, "rest_24.png"),
                    self.canvas.time_2_x(t1) + 2,
                    self.string_id_2_y(self.get_orig_string_by_pos(0).id) + 2.5 * self.string_height,
                    bitmap_scale)
        return draw_pause(mesure, t1 + 24, t2)

      if t2 >= t1 + 18:
        x = self.canvas.time_2_x(t1) + 2
        y = self.string_id_2_y(self.get_orig_string_by_pos(0).id) + 2.5 * self.string_height
        draw_bitmap(self.canvas, ctx, os.path.join(globdef.DATADIR, "rest_12.png"), x, y, bitmap_scale)
        #ctx.arc(x + 9, y + 16, 1.5, 0, 2.0 * math.pi)
        #ctx.fill()
        ctx_drawEllipse(ctx, x + 8.25 * self.scale, y + 15.25 * self.scale, 2.5 * self.scale, 2.5 * self.scale)
        return draw_pause(mesure, t1 + 18, t2)
      
      if t2 >= t1 + 12:
        draw_bitmap(self.canvas, ctx,
                    os.path.join(globdef.DATADIR, "rest_12.png"),
                    self.canvas.time_2_x(t1) + 2,
                    self.string_id_2_y(self.get_orig_string_by_pos(0).id) + 2.5 * self.string_height,
                    bitmap_scale)
        return draw_pause(mesure, t1 + 12, t2)
        
    while mesure.time < t2:
      while (t < mesure.end_time()) and (t < t2):
        note = self.partition.note_before(t + 1)
        if note and (t < note.end_time()):
          t = advance_t(t, note.end_time())
          
        end_pause = mesure.end_time()
        next = self.partition.note_after(t)
        if next and (end_pause > next.time): end_pause = next.time
        if end_pause > t:
          draw_pause(mesure, t, min(end_pause, t2))
          t = end_pause
          
      mesure_id += 1
      if mesure_id >= len(self.partition.song.mesures): break
      mesure = self.partition.song.mesures[mesure_id]
      
      
      
class StaffString(object):
  def __init__(self, drawer, base_note, line_style, alteration, draw_alteration, pos):
    self.drawer              = drawer
    self.base_note           = base_note
    self.line_style          = line_style
    self.alteration          = alteration
    self.draw_alteration     = draw_alteration
    self.pos                 = pos
    
    drawer.value_2_string[base_note] = self
    drawer.strings.append(self)
    
  def value_2_text(self, note):        return "o"
  def text_2_value(self, note, text):  return self.base_note + self.alteration
  
  def __str__(self): return _(self.__class__.__name__) % note_label(self.base_note, 1)
  
  def width(self):
    if   self.line_style == 0: return -1
    elif self.line_style == 1: return 8
    return 9
  
  def color(self): return "black"

class LyricsDrawer(Drawer):
  reduced_fonts = []
  def __init__(self, canvas, lyrics, compact = False):
    Drawer.__init__(self, canvas, compact)
    
    if not self.reduced_fonts:
      font_size = self.canvas.default_font_size
      while font_size > 0:
        font = qtgui.QFont("Sans", font_size)
        metrics = qtgui.QFontMetrics(font)
        self.reduced_fonts.append((font, metrics))
        font_size -= 1
        
    self.last_undoable = None
    self.lyrics  = lyrics
    self.x0      = canvas.start_x + 2
    self.start_y = 0
    self.melody  = None
    self.set_text_size_timer = qtcore.QTimer()
    self.set_text_size_timer.setSingleShot(True)
    self.set_text_size_timer.timeout.connect(self.set_text_size)
    self.update_melody_timer = qtcore.QTimer()
    self.update_melody_timer.setSingleShot(True)
    self.update_melody_timer.timeout.connect(self.update_melody)
    
    self.text = qtwidgets.QTextEdit()
    self.text.setPlaceholderText(_("Type lyrics here..."))
    self.text.setDocument(qtgui.QTextDocument(lyrics.text))
    self.text.insertFromMimeData = self.on_text_paste
    self.text.focusInEvent       = self.on_text_focus
    self.text.focusOutEvent      = self.on_text_unfocus
    self.text.keyPressEvent      = self.on_text_key_press
    self.text.cursorPositionChanged.connect(self.on_move_cursor)
    self.text.textChanged.connect(self.on_text_changed)
    self.text.setLineWrapMode(qtwidgets.QTextEdit.NoWrap)
    self.text.setHorizontalScrollBarPolicy(qtcore.Qt.ScrollBarAlwaysOff)
    self.text.setVerticalScrollBarPolicy(qtcore.Qt.ScrollBarAlwaysOff)
    self.text.setFrameStyle(0)
    self.text.viewport().setAutoFillBackground(False)
    
    self.fixed = qtwidgets.QWidget()
    self.fixed.setLayout(FixedLayout())
    self.fixed.layout().addWidget(self.text)
    self.canvas.viewport().layout().addWidget(self.fixed)
    
    self.canvas.partition_2_drawer[lyrics] = self
    self.update_melody()
    
  def destroy(self):
    self.fixed.layout().removeWidget(self.text)
    self.canvas.viewport().layout().removeWidget(self.fixed)
    self.text.setParent(None)
    self.fixed.setParent(None)
    self.text.destroy()
    self.fixed.destroy()
    Drawer.destroy(self)
    
  def on_move_cursor(self): self.scroll_if_needed()
  
  def scroll_if_needed(self):
    if self.text.hasFocus():
      hscroll = self.canvas.horizontalScrollBar()
      cursor_x = self.text.cursorRect(self.text.textCursor()).x()
      cursor_x = cursor_x + self.canvas.start_x + 2 + self.x0 - self.canvas.x
      if   cursor_x < 40 + self.canvas.start_x:
        hscroll.setValue(max(0, hscroll.value() + int(cursor_x - 40 - self.canvas.start_x)))
      elif cursor_x > self.canvas.width - 60:
        hscroll.setValue(min(hscroll.maximum() + hscroll.pageStep(), hscroll.value() + int(cursor_x - (self.canvas.width - 60))))
        
  def on_text_paste(self, mime_data):
    text = mime_data.text().replace(" ", "\t").replace("-", "--\t").replace("\n", "\\\\\t").replace("\\\\\t\\\\", "\\\\")
    self.text.insertPlainText(text)
    
  def on_text_changed(self):
    old_text = self.lyrics.text
    new_text = self.text.document().toPlainText()

    if old_text == new_text: return
    
    size_changed = old_text.count("\n") != new_text.count("\n")

    def set_text(text):
      self.lyrics.text = text
      current = self.text.document().toPlainText()
      if current != text:
        self.text.textChanged.disconnect(self.on_text_changed)
        self.text.document().setPlainText(text)
        self.text.textChanged.connect(self.on_text_changed)
        self.set_text_size() # Not delayed, because the set_text remove all the precendent text tags !
      else:
        self.delayed_set_text_size()
      if size_changed: self.canvas.render_all()
      
    def do_it  (): set_text(new_text)
    def undo_it(): set_text(old_text)

    if self.canvas.main.undo_stack.undoables: previous_undoable = self.canvas.main.undo_stack.undoables[-1]
    else:                                     previous_undoable = None
    
    undoable = UndoableOperation(do_it, undo_it, _("edit lyrics"), self.canvas.main.undo_stack)
    
    if self.last_undoable and (self.last_undoable is previous_undoable):
      undoable.coalesce_with(previous_undoable)
    self.last_undoable = undoable
    
    self.scroll_if_needed()
    
  def on_text_focus(self, event):
    qtwidgets.QTextEdit.focusInEvent(self.text, event)
    self.canvas.deselect_all()
    self.canvas.main.selected_partition = self.lyrics
    self.canvas.main.set_note_menus_enabled(False)
    
  def on_text_unfocus(self, event):
    qtwidgets.QTextEdit.focusOutEvent(self.text, event)
    self.canvas.main.set_note_menus_enabled(True)
    
  def on_text_key_press(self, event):
    if event.modifiers() == qtcore.Qt.ControlModifier:
      if   event.key() == qtcore.Qt.Key_Space:
        event = qtgui.QKeyEvent(qtcore.QEvent.KeyPress, qtcore.Qt.Key_Space, qtcore.Qt.NoModifier, " ", event.isAutoRepeat(), 1)
      elif event.key() == qtcore.Qt.Key_Minus:
        event = qtgui.QKeyEvent(qtcore.QEvent.KeyPress, qtcore.Qt.Key_Minus, qtcore.Qt.NoModifier, "-", event.isAutoRepeat(), 1)
    else:
      if   event.key() == qtcore.Qt.Key_Space:
        event = qtgui.QKeyEvent(qtcore.QEvent.KeyPress, qtcore.Qt.Key_Tab, qtcore.Qt.NoModifier, "\t", event.isAutoRepeat(), 1)
      elif event.key() == qtcore.Qt.Key_Minus:
        event = qtgui.QKeyEvent(qtcore.QEvent.KeyPress, qtcore.Qt.Key_Tab, qtcore.Qt.NoModifier, "-\t", event.isAutoRepeat(), 1)
        
    qtwidgets.QTextEdit.keyPressEvent(self.text, event)
      
  def partition_listener(self, partition, type, new, old): pass
  
  def melody_note_listener(self, obj, type, new, old): self.delayed_update_melody()
    
  def delayed_update_melody(self):
    self.update_melody_timer.stop()
    self.update_melody_timer.start(120)
    
  def delayed_set_text_size(self):
    self.set_text_size_timer.stop()
    self.set_text_size_timer.start(120)
    
  def update_melody(self):
    melody = self.melody = self.lyrics.get_melody()
    
    self.sizes = []
    if melody and melody.notes:
      x0 = int(2 + self.canvas.time_2_x(melody.notes[0].time) - self.canvas.start_x + self.canvas.x)
      tabs = []
      previous_time = melody.notes[0].time
      i = 0
      x = 0
      for note in melody.notes[1:]:
        if note.time == previous_time: continue
        if note.duration_fx == "appoggiatura": continue
        note_x = self.canvas.time_2_x(note.time) - self.canvas.start_x + self.canvas.x
        if i == 0: self.sizes.append(note_x - x - x0)
        else:      self.sizes.append(note_x - x)
        tabs.append(qtgui.QTextOption.Tab(note_x - x0, qtgui.QTextOption.LeftTab))
        x = note_x
        i += 1
        previous_time = note.time
      block_format = qtgui.QTextBlockFormat()
      block_format.setTabPositions(tabs)
      cursor = qtgui.QTextCursor(self.text.document())
      cursor.select(qtgui.QTextCursor.Document)
      cursor.setBlockFormat(block_format)

      self.sizes.append(500)
      
      if self.x0 != x0:
        self.x0 = x0
        self.canvas.render_all()
    self.delayed_set_text_size()
    
  def set_text_size(self):
    self.text.textChanged.disconnect(self.on_text_changed)
    cursor = qtgui.QTextCursor(self.text.document())
    cursor.select(qtgui.QTextCursor.Document)
    cursor.setCharFormat(qtgui.QTextCharFormat())
    default_font = self.reduced_fonts[0][0]
    
    offset = 0
    for line in self.lyrics.text.split("\n"):
      i = 0
      for piece in line.split("\t"):
        if i < len(self.sizes):
          max_width = self.sizes[i] - 7.0 * self.scale
          
          for reduced_font, reduced_metrics in self.reduced_fonts:
            width = reduced_metrics.width(piece)
            if width < max_width: break
            
          if not reduced_font is default_font:
            char_format = qtgui.QTextCharFormat()
            char_format.setFont(reduced_font)
            
            cursor.setPosition(offset, qtgui.QTextCursor.MoveAnchor)
            cursor.setPosition(offset + len(piece), qtgui.QTextCursor.KeepAnchor)
            cursor.setCharFormat(char_format)
            
        offset += len(piece) + 1 # +1 for \t or \n
        i      += 1
        
    self.text.textChanged.connect(self.on_text_changed)
    
  def draw(self, ctx, x, y, width, height, drag = 0):
    text_height = max(editor_qt.SMALL_ICON_SIZE * self.scale, (self.lyrics.text.count("\n") + 2) * self.canvas.default_line_height)
    if Drawer.draw(self, ctx, x, y, width, height, drag):
      ctx_drawText(ctx, 3.0 * self.scale, self.y + self.canvas.default_ascent, self.lyrics.header)
      self.start_y = self.canvas.default_line_height
      self.height = self.start_y + text_height
      
      ctx.setRenderHint(qtgui.QPainter.Antialiasing, False)
      ctx_drawRect(ctx, self.canvas.start_x - 1, self.y + self.start_y, 2, self.height - self.start_y)
      ctx.setRenderHint(qtgui.QPainter.Antialiasing, True)
      
      draw_bitmap(self.canvas, ctx,
                  description(self.lyrics.__class__).icon_filename_for(self.lyrics),
                  4 * self.scale,
                  int(self.y + self.start_y // 2 + self.height // 2 - (editor_qt.SMALL_ICON_SIZE * self.scale) // 2),
                  0.5 * self.scale)
      
    self.canvas.viewport().layout().move_resize_widget(self.fixed, self.canvas.start_x + 2, self.y + self.start_y, self.canvas.width - self.canvas.start_x + 2, text_height)
    self.fixed.layout().move_resize_widget(self.text, self.x0 - self.canvas.x, 0, max(sum(self.sizes), 1300), text_height)
      
    
  def on_button_press(self, *args): self.text.setFocus()

    
  


def new_layout(ctx, font = "Sans 12"):
  layout = ctx.create_layout()
  layout.set_font_description(pango.FontDescription(font))
  ctx.update_layout(layout)
  return layout
  


_BITMAP_CACHE = {}

def draw_bitmap(canvas, ctx, bitmap_filename, x, y, scale = 1.0):
  image = _BITMAP_CACHE.get(bitmap_filename)
  if not image: image = _BITMAP_CACHE[bitmap_filename] = qtgui.QPixmap(bitmap_filename)
  ctx_drawPixmap(ctx, x, y, image.width() * scale, image.height() * scale, image)
  

def cmp(a, b):
  if    a < b: return -1
  elif a == b: return 0
  return 1
