# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2011 Jean-Baptiste LAMY -- jibalamy@free.fr
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

from editobj3.undoredo import *

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui

import songwrite3.model     as model
import songwrite3.globdef   as globdef
import songwrite3.canvas    as canvas
from songwrite3.plugins.chord.chord import ChordManager, TablatureChordManager, LyreChordManager, PianoChordManager, AccordionChordManager
from songwrite3.canvas import ctx_drawText, ctx_drawText2, ctx_drawLine, ctx_drawRect, ctx_drawEllipse, ctx_drawPixmap

def set_chord(canvas, partition, chord_manager, times, base, second = 0, third = 1, fourth = 0, fifth = 7, sixth = 0, seventh = 0):
  if third == 1: third = chord_manager.choose_third(partition, base)
    #if ((base + 4 - model.OFFSETS[partition.tonality]) % 12) in model.NOTES: third = 4
    #else:                                                                    third = 3
  if not isinstance(times, dict): # times should be a dict mapping each time to the reference note for it
    times2 = {}
    for time in times:
      notes = partition.notes_at(time)
      times2[time] = notes[0]
    times = times2
  values, frets  = chord_manager.create(base, second, third, fourth, fifth, sixth, seventh)
  saved          = {}
  saved_duration = {}
  removed        = []
  new_notes      = []
  def do_it(saved_duration = saved_duration):
    for time, ref in times.items():
      notes = partition.notes_at(time)
      i = 0
      chord_notes = []
      for value, string_id in values:
        if i < len(notes):
          saved[notes[i]] = notes[i].value, getattr(notes[i], "string_id", 0)
          notes[i].value = value
          if string_id != -1:
            notes[i].string_id = string_id
          chord_notes.append(notes[i])
          if canvas:
            canvas.auto_update_duration(notes[i], saved_duration)
            canvas.auto_update_duration(notes[i].partition.note_after(notes[i]), saved_duration)
          i += 1
        else:
          new_note = model.Note(partition, time, ref.duration, value, ref.volume)
          if string_id != -1:
            new_note.string_id  = string_id
          new_note.fx           = ref.fx
          new_note.link_fx      = ref.link_fx
          new_note.duration_fx  = ref.duration_fx
          new_note.strum_dir_fx = ref.strum_dir_fx
          new_notes  .append(new_note)
          chord_notes.append(new_note)
      if len(values) < len(notes):
        removed.extend(notes[len(values) - len(notes) :])
    partition.remove(*removed)
    partition.add_note(*new_notes)
    if canvas:
      for new_note in new_notes:
        canvas.auto_update_duration(new_note, saved_duration)
        canvas.auto_update_duration(new_note.partition.note_after(new_note), saved_duration)
      canvas.deselect_all()
      for note in chord_notes: canvas.partition_2_drawer[partition].select_note(note)
      
  def undo_it(saved_duration = saved_duration):
    for note, (value, string_id) in saved.items():
      note.value     = value
      note.string_id = string_id
    if removed  : partition.add_note(*removed)
    if new_notes: partition.remove  (*new_notes)
    if canvas: canvas.restore_saved_duration(saved_duration)
    saved         .clear()
    saved_duration.clear()
    removed       .__imul__(0)
    new_notes     .__imul__(0)
  return do_it, undo_it


class ChordDrawer(canvas.PartitionDrawer):
  avoid_repeat      = 1
  always_draw_stems = 1
  need_extra_space_for_strum_dir = 0
  def __init__(self, canvas_, partition, compact = False):
    canvas.PartitionDrawer.__init__(self, canvas_, partition, compact)
    self.strings = [SingleString(self)]
    self.string_height     = self.canvas.default_line_height * 1.3
    self.stem_extra_height = self.canvas.default_line_height
    self.chord_manager     = self.ChordManager(partition)
    self.last_chord_name   = None
    self.last_chord_mesure = None
    self.note_offset_x     = 3.0 * self.scale
    
  def config_listener(self, obj, type, new, old):
    canvas.PartitionDrawer.config_listener(self, obj, type, new, old)
    if type is object:
      if   (new.get("ENGLISH_CHORD_NAME") != old.get("ENGLISH_CHORD_NAME")):
        self.chord_manager = self.ChordManager(self.partition)
        self.canvas.render_all()
        
  def partition_listener(self, partition, type, new, old):
    canvas.PartitionDrawer.partition_listener(self, partition, type, new, old)
    if type is object:
      if   (new.get("tonality") != old.get("tonality")):
        self.chord_manager = self.ChordManager(self.partition)
        self.canvas.render_all()
        
  def on_touchscreen_new_note(self, event): return False
  
  def note_width(self, note): return 9.0 * self.scale
  
  def select_note(self, note):
    notes = self.partition.notes_at(note)
    if not note in notes:
      self.canvas.add_selection(note, *self.note_dimensions(note))
    for note in notes:
      self.canvas.add_selection(note, *self.note_dimensions(note))
      
  def on_key_press(self, event):
    keyval = event.key()
    if   qtcore.Qt.Key_A <= keyval <= qtcore.Qt.Key_G: # a-g
      value = model.NOTES[(keyval - qtcore.Qt.Key_A + 5) % 7]
      if value in model.TONALITIES[self.partition.tonality]:
        if model.TONALITIES[self.partition.tonality][0] == model.DIESES[0]:
          value += 1
        else:
          value -= 1
          
      times = {}
      for note in self.canvas.selections: times[note.time] = note
      do_it, undo_it = set_chord(self.canvas, self.partition, self.chord_manager, times, value)
      UndoableOperation(do_it, undo_it, _("add chord"), self.canvas.main.undo_stack)
      return 1
    
    elif keyval == qtcore.Qt.Key_M: # m
      self.toggle_major()
      return 1
    
    elif qtcore.Qt.Key_0 <= keyval <= qtcore.Qt.Key_9: # Numbers
      nb = keyval - qtcore.Qt.Key_0
      if nb == 5: self.toggle_5()
      if nb == 7: self.toggle_7()
      return 1
    
  def toggle_major(self):
    times = {}
    for note in self.canvas.selections: times[note.time] = 1
    for time in times:
      notes      = self.partition.notes_at(time)
      rel_values = frozenset([note.value for note in notes])
      chord      = self.chord_manager.identify(rel_values)
      if chord:
        third = chord.identified_notes[2]
        if third == 3: third = 4; break
        else:          third = 3; break
    else: third = 4
    do_its   = []
    undo_its = []
    for time in times:
      notes      = self.partition.notes_at(time)
      rel_values = frozenset([note.value for note in notes])
      chord      = self.chord_manager.identify(rel_values)
      v = [value or 0 for value in chord.identified_notes]
      #do_it1, undo_it1 = self.set_chord([time], chord.base, v[1], third, v[3], v[4], v[5], v[6], return_func = 1)
      do_it1, undo_it1 = set_chord(self.canvas, self.partition, self.chord_manager, [time], chord.base, v[1], third, v[3], v[4], v[5], v[6])
      do_its  .append(  do_it1)
      undo_its.append(undo_it1)
    def do_it():
      for func in do_its: func()
    def undo_it():
      for func in undo_its: func()
    UndoableOperation(do_it, undo_it, _("add chord"), self.canvas.main.undo_stack)
    
  def toggle_5(self):
    times = {}
    for note in self.canvas.selections: times[note.time] = 1
    for time in times:
      notes      = self.partition.notes_at(time)
      rel_values = frozenset([note.value for note in notes])
      chord      = self.chord_manager.identify(rel_values)
      if chord:
        third = chord.identified_notes[2]
        if third: third = 0; break
    else: third = 1
    
    do_its   = []
    undo_its = []
    for time in times:
      notes      = self.partition.notes_at(time)
      rel_values = frozenset([note.value for note in notes])
      chord      = self.chord_manager.identify(rel_values)
      v = [value or 0 for value in chord.identified_notes]
      do_it1, undo_it1 = set_chord(self.canvas, self.partition, self.chord_manager, [time], chord.base, v[1], third, v[3], v[4], v[5], v[6])
      do_its  .append(  do_it1)
      undo_its.append(undo_it1)
    def do_it():
      for func in do_its: func()
    def undo_it():
      for func in undo_its: func()
    UndoableOperation(do_it, undo_it, _("add chord"), self.canvas.main.undo_stack)
    
  def toggle_7(self):
    times = {}
    for note in self.canvas.selections: times[note.time] = 1
    for time in times:
      notes      = self.partition.notes_at(time)
      rel_values = frozenset([note.value for note in notes])
      chord      = self.chord_manager.identify(rel_values)
      if chord:
        seventh = chord.identified_notes[6]
        if seventh: seventh = 0; break
    else: seventh = 10
    do_its   = []
    undo_its = []
    for time in times:
      notes      = self.partition.notes_at(time)
      rel_values = frozenset([note.value for note in notes])
      chord      = self.chord_manager.identify(rel_values)
      v = [value or 0 for value in chord.identified_notes]
      #do_it1, undo_it1 = self.set_chord([time], chord.base, v[1], v[2], v[3], v[4], v[5], seventh, return_func = 1)
      do_it1, undo_it1 = set_chord(self.canvas, self.partition, self.chord_manager, [time], chord.base, v[1], v[2], v[3], v[4], v[5], seventh)
      do_its  .append(  do_it1)
      undo_its.append(undo_it1)
    def do_it():
      for func in do_its: func()
    def undo_it():
      for func in undo_its: func()
    UndoableOperation(do_it, undo_it, _("add chord"), self.canvas.main.undo_stack)
      
  # No "string" notion in chord notation!
  def note_string_id   (self, note ): return 0
  def default_string_id(self, value): return 0
  def y_2_string_id(self, y, force = 0):
    if force:
      if   self.y + self.start_y > y: return -1
      elif y > self.y + self.height:  return  1
      return 0
    else:
      if self.y + self.start_y <= y <= self.y + self.height: return 0
      return None
  def string_id_2_y(self, string_id = 0):
    return self.y + self.start_y + self.stem_extra_height + self.string_height // 2
  
  def draw(self, ctx, x, y, width, height, drag = 0, draw_icon = 1):
    if self.compact:
      canvas.PartitionDrawer.draw(self, ctx, x, y, width, height, drag, 0, -11.0)
    else:
      canvas.PartitionDrawer.draw(self, ctx, x, y, width, height, drag, 0, -11.0)
    
  def draw_mesure(self, ctx, time, mesure, y, height):
    canvas.PartitionDrawer.draw_mesure(self, ctx, time, mesure, y, height, False)
    #pass
  
  def draw_strings(self, ctx, x, y, width, height):
    self.height = int(self.start_y + self.stem_extra_height + self.string_height + self.stem_extra_height_bottom + 1)
    self.last_chord_name = None
    
  def render_note(self, note):
    mesure = self.canvas.song.mesure_at(note)
    if mesure.rythm2 == 8: time1 = (note.link_start() // 144) * 144; time2 = max(note.link_end(), time1 + 144)
    else:                  time1 = (note.link_start() //  96) *  96; time2 = max(note.link_end(), time1 +  96)
    self.canvas.render_pixel(
      self.canvas.time_2_x(time1) - 10.0 * self.scale,
      self.y,
      (time2 - time1) * self.canvas.zoom + 50.0 * self.scale,
      self.height + self.canvas.default_line_height // 2 + self.canvas.default_ascent // 2,
      )
    
  def note_text(self, note): return "_"
  
  def draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure = None, previous_time = -32000, next_time = 32000):
    x = x + self.canvas.default_line_height // 2
    canvas.PartitionDrawer.draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure, previous_time, next_time)
    
  def draw_stem_and_beam_for_chord(self, ctx, notes, notes_y, previous, next, appo = 0):
    self.draw_chord(ctx, notes, notes_y, previous, next, appo)
      
  def draw_chord(self, ctx, notes, notes_y, previous, next, appo):
    ctx.setPen(self.note_color(notes[0]))
    rel_values = frozenset([note.value for note in notes])
    if rel_values == frozenset([0]):
      ctx_drawText(ctx, self.canvas.time_2_x(notes[0].time) + self.note_offset_x, self.y + self.start_y + 2 * self.stem_extra_height, "_")
    else:
      chord = self.chord_manager.identify(rel_values)
      if chord: name = chord.name
      else:     name = "?"
      mesure = self.partition.song.mesure_at(notes[0].time)
      if (name != self.last_chord_name) or (mesure != self.last_chord_mesure):
        max_width = 99999
        if next:
          next_notes = self.partition.notes_at(next.time)
          rel_values = frozenset([note.value for note in next_notes])
          if rel_values:
            chord = self.chord_manager.identify(rel_values)
            if chord and ((not self.avoid_repeat) or (chord.name != name)):
              max_width = (self.canvas.time_2_x(next.time) - self.canvas.time_2_x(notes[0].time)) - 3 * self.scale
        ctx_drawText2(ctx, 
          self.canvas.time_2_x(notes[0].time) + self.note_offset_x,
          self.y + self.start_y + 2 * self.stem_extra_height - self.canvas.default_ascent,
          max_width,
          999,
          0,
          name,
        )
        
        if self.avoid_repeat:
          self.last_chord_name   = name
          self.last_chord_mesure = mesure
    if not self.draw_strum_direction(ctx, notes):
      canvas.PartitionDrawer.draw_stem_and_beam_for_chord(self, ctx, notes, notes_y, previous, next, appo)
    ctx.setPen(qtcore.Qt.black)
    
  def draw_strum_direction(self, ctx, notes, offset_x = 0.0):
    return canvas.PartitionDrawer.draw_strum_direction(self, ctx, notes, offset_x + self.note_offset_x)
    
  def draw_note(self, ctx, note, string_id, y): pass
  

class SingleString(object):
  def __init__(self, drawer, notation_pos = -1):
    self.drawer       = drawer
    self.notation_pos = notation_pos
    
  base_note = 0
  
  def text_2_value(self, note, text): return self.base_note
  def value_2_text(self, note): return "/"
  def __str__(self): return "Single string"
  def width(self): return -1
  def on_click_at(self, hole): return "0"
        
    
class TablatureChordDrawer(ChordDrawer):
  ChordManager = TablatureChordManager
  
  
class PianoChordDrawer(ChordDrawer):
  ChordManager = PianoChordManager
  
  
class LyreChordDrawer(ChordDrawer):
  ChordManager = LyreChordManager
  
  
class AccordionChordDrawer(ChordDrawer):
  avoid_repeat = 0
  ChordManager = AccordionChordManager
  
  def __init__(self, canvas_, partition, compact = False):
    ChordDrawer.__init__(self, canvas_, partition, compact)
    self.note_offset_x = 3.0 * self.scale
    
  def drawers_changed(self):
    try:    previous = self.canvas.drawers[self.canvas.drawers.index(self) - 1]
    except: self.left_hand_drawer = None
    else:
      if previous.__class__.__name__ == "AccordionDrawer": self.left_hand_drawer = previous
      else:                                                self.left_hand_drawer = None
    if self.left_hand_drawer: self.show_header = 0
    else:                     self.show_header = 1
    
  def draw(self, ctx, x, y, width, height, drag = 0, draw_icon = 1):
    if self.show_header:
      return canvas.PartitionDrawer.draw(self, ctx, x, y, width, height, drag, 0, -34)
    else:
      #text_width = ctx.text_extents(_("LG"))[2]
      #ctx.move_to(85.0 * self.scale - text_width, self.y + 14.5 * self.scale)
      #ctx.show_text(_("LG"))
      if self.compact:
        ctx_drawText(ctx, 65.0 * self.scale, self.y + 20.0 * self.scale, _("LG"))
        return canvas.PartitionDrawer.draw(self, ctx, x, y, width, height, drag, 0, -10.0)
      else:
        ctx_drawText(ctx, 65.0 * self.scale, self.y + 20.0 * self.scale, _("LG"))
        return canvas.PartitionDrawer.draw(self, ctx, x, y, width, height, drag, 0, -20.0)
      
  def draw_stem_and_beam_for_chord(self, ctx, notes, notes_y, previous, next, appo = 0):
    self.draw_chord(ctx, notes, notes_y, previous, next, appo)
    
  def draw_stem_and_beam(self, ctx, x, note, y1, y2, mesure = None, previous_time = -32000, next_time = 32000):
    pass
    
  def on_key_press(self, event):
    keyval = event.key()
    if (event.modifiers() == qtcore.Qt.ShiftModifier) and (qtcore.Qt.Key_A <= keyval <= qtcore.Qt.Key_G): # A-G
      value = model.NOTES[(keyval - qtcore.Qt.Key_A + 5) % 7]
      if value in model.TONALITIES[self.partition.tonality]:
        if model.TONALITIES[self.partition.tonality][0] == model.DIESES[0]:
          value += 1
        else:
          value -= 1
          
      times = {}
      for note in self.canvas.selections: times[note.time] = note
      do_it, undo_it = set_chord(self.canvas, self.partition, self.chord_manager, times, value, second = 0, third = 0, fourth = 0, fifth = 0, sixth = 0, seventh = 0)
      UndoableOperation(do_it, undo_it, _("add bass"), self.canvas.main.undo_stack)
      return 1
    
    return ChordDrawer.on_key_press(self, event)
    
