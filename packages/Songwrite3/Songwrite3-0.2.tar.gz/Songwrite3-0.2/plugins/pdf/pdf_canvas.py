# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2007-2016 Jean-Baptiste LAMY -- jibalamy@free.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, math, bisect, locale, codecs
from io import StringIO

import editobj3.editor_qt as editor_qt

import songwrite3.model  as model
from   songwrite3.canvas import *

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui


class PDFAdditionalStaffDrawer(StaffDrawer):
  def draw(self, ctx, x, y, width, height, drag = 0):
    self.partition.real_view = self.partition.view
    try:
      self.partition.view = model.GuitarStaffView(self.partition, 0)
      
      StaffDrawer.draw(self, ctx, x, y, width, height, drag)
    finally:
      self.partition.view = self.partition.real_view
      del self.partition.real_view
      
  def draw_note(self, ctx, note, string_id, y):
    if (note.fx == "harmonic") and (self.partition.real_view.use_harmonics_for_octavo): # Lyre use harmonic for second octavo, not as fx
      note.fx = ""
      StaffDrawer.draw_note(self, ctx, note, string_id, y)
      note.fx = "harmonic"
    else:
      StaffDrawer.draw_note(self, ctx, note, string_id, y)
    
    
class PDFLyricsDrawer(Drawer):
  def __init__(self, canvas, lyrics, melody):
    Drawer.__init__(self, canvas)
    
    self.lyrics  = lyrics
    self.melody  = melody
    self.x0      = canvas.start_x + 2
    self.start_y = 0
    
  def draw(self, ctx, x, y, width, height, drag = 0):
    if Drawer.draw(self, ctx, x, y, width, height, drag):
      text_y = self.y + self.start_y + 1 + self.canvas.default_line_height / 2 + self.canvas.default_ascent / 2 - self.canvas.default_descent / 2
      lignes = self.lyrics.text.split("\n")
      
      nb_ligne = 1
      ctx.setPen(qtcore.Qt.black)
      cur_x = 0
      
      reduced_fonts = []
      font_size = self.canvas.default_font_size
      while font_size > 3:
        font = qtgui.QFont("Sans", font_size)
        font = qtgui.QFont(font, ctx.device())
        font.setPixelSize(font_size)
        metrics = qtgui.QFontMetrics(font)
        reduced_fonts.append((font, metrics))
        font_size -= 1
        
      def render_syllabe(syllabe, text_x, text_y, max_width):
        for reduced_font, reduced_metrics in reduced_fonts:
          width = reduced_metrics.width(syllabe)
          if width < max_width: break
        ctx.setFont(reduced_font)
        ctx.drawText(qtcore.QPointF(text_x, text_y), syllabe)
        
      syllabe = ""
      for ligne in lignes:
        syllabes = ligne.replace("\\\\", "").replace("--", "-").split("\t")
        
        melody_notes0 = [note for note in self.melody.notes if not note.duration_fx == "appoggiatura"]
        melody_notes  = []
        previous_time = -1000
        for note in melody_notes0:
          if note.time == previous_time: continue
          melody_notes.append(note)
          previous_time = note.time
          
        nb_skip = 0
        for i in range(min(len(melody_notes), len(syllabes))):
          if nb_skip:
            nb_skip -= 1
            continue
          note    = melody_notes[i]
          if not (self.canvas.time1 <= note.time < self.canvas.time2):
            continue
          
          if syllabe:
            if syllabes[i] in ("_", "_-"):
              max_text_width += note.duration * self.canvas.zoom
              continue
            else:
              render_syllabe(syllabe, text_x, text_y, max_text_width)
              
          syllabe = syllabes[i]
          if not syllabe: continue
          
          text_x = self.canvas.time_2_x(note.time) + 1
          if text_x < x: continue
          if text_x > x + width: break
          
          if text_x <= cur_x: # Need breakline !
            nb_ligne += 1
            text_y   += self.canvas.default_line_height
          max_text_width = note.duration * self.canvas.zoom - 3 * self.scale
          
          cur_x = text_x
          
      if syllabe: render_syllabe(syllabe, text_x, text_y, max_text_width)
      
      self.height = self.start_y + nb_ligne * self.canvas.default_line_height + 1
      ctx.setFont(self.canvas.default_font)

    
class PDFCanvas(BaseCanvas):
  is_gui_interface = 0
  def __init__(self, song):
    BaseCanvas.__init__(self, song)
    
    self.set_default_font_size(song.printfontsize)
    self.update_mesure_size()
    
  def render(self, filename, x, width, time1, time2, zoom):
    self.filename = filename
    self.time1    = time1
    self.time2    = time2
    self.zoom     = zoom
    self.x        = x
    self.width    = width
    self.height   = 10000
    
    self.drawers  = []
    
    for i in range(2): # First and second pass for computing size
      buffer = qtcore.QBuffer()
      buffer.open(qtcore.QIODevice.WriteOnly)
      self.draw(buffer)
    self.draw(self.filename)
    
    
  def set_default_font_size(self, size, device = None):
    BaseCanvas.set_default_font_size(self, size, device or self.create_pdf_device(qtcore.QBuffer(), 10, 10))
    
  def render_all(self): pass
  
  def create_pdf_device(self, filename, width, height):
    surface = qtgui.QPdfWriter(filename)
    
    if hasattr(qtgui, "QPageLayout"): # Qt >= 5.3
      surface.setResolution(72)
      page_layout = qtgui.QPageLayout()
      page_layout.setMode(qtgui.QPageLayout.FullPageMode)
      page_layout.setMargins(qtcore.QMarginsF(0.0, 0.0, 0.0, 0.0))
      page_layout.setPageSize(qtgui.QPageSize(qtcore.QSize(int(min(width, height)), int(max(width, height))), None, qtgui.QPageSize.ExactMatch))
      if width > height: page_layout.setOrientation(qtgui.QPageLayout.Landscape)
      else:              page_layout.setOrientation(qtgui.QPageLayout.Portrait)
      surface.setPageLayout(page_layout)
      
    else: # Qt <= 5.2 
      surface.setMargins(qtgui.QPagedPaintDevice.Margins())
      #surface.setPageSizeMM(qtcore.QSizeF(width / 72 * 25.4, height / 72 * 25.4))
      surface.setPageSizeMM(qtcore.QSizeF(width / 1200.0 * 25.4, height / 1200.0 * 25.4))
      
    return surface
  
  def draw(self, filename):
    drawer = None
    
    surface = self.create_pdf_device(filename, self.width, self.height)
    self.set_default_font_size(self.song.printfontsize, surface)
    
    ctx = qtgui.QPainter(surface)
    ctx.setRenderHints(qtgui.QPainter.Antialiasing | qtgui.QPainter.TextAntialiasing | qtgui.QPainter.SmoothPixmapTransform)
    ctx.setBrush(qtcore.Qt.black)
    ctx.setFont(self.default_font)
    
    lyricss = []
    def add_lyrics():
      text = "\n".join([lyrics.text for lyrics in lyricss if lyrics.show_all_lines_on_melody])
      if text:
        cumulated_lyrics = model.Lyrics(self.song, text, _("Lyrics"))
        drawer = PDFLyricsDrawer(self, cumulated_lyrics, melody)
        self.drawers.append(drawer)
        
      else:
        syllabess = [line.split("\t") for lyrics in lyricss for line in lyrics.text.split("\n") if not lyrics.show_all_lines_on_melody]
        
        if syllabess:
          cummulated_syllabes = [""] * len([note for note in melody.notes if not note.duration_fx == "appoggiatura"])
          for i in range(len(cummulated_syllabes)):
            for syllabes in syllabess:
              if (i < len(syllabes)) and syllabes[i]:
                cummulated_syllabes[i] = syllabes[i]
                break
          cumulated_lyrics = model.Lyrics(self.song, "\t".join(cummulated_syllabes), _("Lyrics"))
          drawer = PDFLyricsDrawer(self, cumulated_lyrics, melody)
          self.drawers.append(drawer)
          
      lyricss.__imul__(0)
      
    if not self.drawers:
      for partition in self.song.partitions:
        if   isinstance(partition, model.Partition):
          add_lyrics()
          melody = partition
          if not partition.notes_at(self.time1, self.time2 - 1): continue
          
        if   getattr(partition, "print_with_staff_too", 0) and not isinstance(partition.view, model.StaffView):
          drawer = PDFAdditionalStaffDrawer(self, partition, compact = 1)
          self.drawers.append(drawer)
          
        if isinstance(partition, model.Lyrics): lyricss.append(partition)
        else: drawer = partition.view.get_drawer(self, compact = 1)
        if drawer:
          if   getattr(partition, "print_with_staff_too", 0): drawer.show_header = 0
          self.drawers.append(drawer)
          drawer = None
      add_lyrics()
      
      for drawer in self.drawers: drawer.drawers_changed()
      
    if not self.drawers:
      for partition in self.song.partitions:
        if   isinstance(partition, model.Partition):
          add_lyrics()
          melody = partition
          
        if   getattr(partition, "print_with_staff_too", 0) and not isinstance(partition.view, model.StaffView):
          drawer = PDFAdditionalStaffDrawer(self, partition, compact = 1)
          self.drawers.append(drawer)
          
        if isinstance(partition, model.Lyrics): lyricss.append(partition)
        else: drawer = partition.view.get_drawer(self, compact = 1)
        if drawer:
          if   getattr(partition, "print_with_staff_too", 0): drawer.show_header = 0
          self.drawers.append(drawer)
          drawer = None
        break # Only first
      
      add_lyrics()
      
      for drawer in self.drawers: drawer.drawers_changed()
      
    x     = self.start_x
    width = self.width
    y     = 0
    y1    = 0
    y2    = 0
    dy    = 0
    total_height = 0
    for drawer in self.drawers:
      drawer.y = dy
      drawer.draw(ctx, x, y, width, self.height)
      dy           += drawer.height
      total_height += drawer.height
      
    # Show mesure number at the beginning
    if self.drawers and isinstance(self.drawers[0], PartitionDrawer):
      mesure_number = str(1 + self.song.mesures.index(self.song.mesure_at(self.time1)))
      ctx.setFont(self.small_font)
      text_size = ctx.fontMetrics().size(0, mesure_number)
      ctx.drawText(qtcore.QPointF(
        self.start_x - text_size.width(),
        self.drawers[0].y + self.drawers[0].start_y + self.drawers[0].stem_extra_height - text_size.height() // 2),
        mesure_number)
      
    for drawer in self.drawers:
      if hasattr(drawer, "strings") and (len(drawer.strings) > 1):
        y1 = drawer.y + drawer.start_y + drawer.stem_extra_height + drawer.string_height * 1.5
        break
    for drawer in reversed(self.drawers):
      if hasattr(drawer, "strings") and (len(drawer.strings) > 1):
        y2 = drawer.y + drawer.start_y + drawer.stem_extra_height + drawer.string_height * 1.5
        break
      
    mesure = self.song.mesure_at(self.time1)
    x = self.start_x
    #x = self.time_2_x(self.time1)
    #x = self.start_x - self.x + self.time1 * self.zoom
    ctx.drawLine(qtcore.QPointF(x, y1), qtcore.QPointF(x, y2))
    
    ctx.end()
    self.height = total_height
