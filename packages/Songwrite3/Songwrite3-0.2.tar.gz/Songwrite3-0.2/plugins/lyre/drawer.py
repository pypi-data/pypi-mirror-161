# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2008-2016 Jean-Baptiste LAMY -- jibalamy@free.fr
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

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui

import songwrite3.model     as model
import songwrite3.canvas    as canvas_module

from songwrite3.canvas import ctx_drawText, ctx_drawText2, ctx_drawLine, ctx_drawRect, ctx_drawEllipse, ctx_drawPixmap



class LyreDrawer(canvas_module.TablatureDrawer):
  def __init__(self, canvas, partition, compact = False):
    canvas_module.TablatureDrawer.__init__(self, canvas, partition)
    self.compact = compact
    if compact: self.string_height = canvas.default_line_height / 1.5
    else:       self.string_height = 0.8 * canvas.default_line_height + 2 * self.scale
    self.note_offset_x =  0.66 * self.string_height
    self.note_offset_y = -10.0 * self.scale #-self.string_height // 22.0
    
  def mouse_motion_note(self, value, delta): return value + delta
  
  def note_listener(self, note, type, new, old):
    if type is object:
      if   (new.get("fx", "") == "harmonic") and (old.get("fx", "") != "harmonic"):
        string_value = self.strings[self.note_string_id(note)].base_note
        if abs(string_value - note.value) < 6: note.value += 12
        
      elif (new.get("fx", "") != "harmonic") and (old.get("fx", "") == "harmonic"):
        string_value = self.strings[self.note_string_id(note)].base_note
        if abs(string_value - note.value) >= 6: note.value -= 12
        
      elif new["value"] != old["value"]:
        string_value = self.strings[self.note_string_id(note)].base_note
        diff = abs(string_value - note.value)
        if   (diff >= 6) and (note.fx == ""):         note.set_fx("harmonic")
        elif (diff <  6) and (note.fx == "harmonic"): note.set_fx("")
        
    canvas_module.TablatureDrawer.note_listener(self, note, type, new, old)
    
  create_cursor = canvas_module.PartitionDrawer.create_cursor
  
  def note_text(self, note):
    if note.fx == "dead":
      return " "
    s = self.strings[self.note_string_id(note)].value_2_text(note)
    if (not note is self.canvas.cursor) and (s != "0") and (s != "12"): return s
    if note.fx == "harmonic":
      if note is self.canvas.cursor: return "_◆"
      return "◆"
    if note is self.canvas.cursor: return "_"
    return "●"
    
  def note_previous(self, note):
    string_id = self.note_string_id(note)
    while 1:
      note = note.previous()
      if not note: return None
      if self.note_string_id(note) == string_id: return note
      
  def draw_note(self, ctx, note, string_id, y):
    x      = self.canvas.time_2_x(note.time)
    string = self.strings[string_id]
    color  = self.note_color(note)
    
    ctx.save()
    ctx.setPen(color)
    ctx.setBrush(color)
    if   note.fx == "harmonic":
      if note.duration_fx == "appoggiatura": # White appoggiatura should never exist !
        ctx.drawPolygon(
          qtcore.QPointF(x + 0.35 * self.string_height, y),
          qtcore.QPointF(x + 0.6  * self.string_height, y + 0.25 * self.string_height),
          qtcore.QPointF(x + 0.85 * self.string_height, y),
          qtcore.QPointF(x + 0.6  * self.string_height, y - 0.25 * self.string_height),
        )
      else:
        ctx.drawPolygon(
          qtcore.QPointF(x + 0.2 * self.string_height, y),
          qtcore.QPointF(x + 0.6 * self.string_height, y + 0.4 * self.string_height),
          qtcore.QPointF(x + 1.0 * self.string_height, y),
          qtcore.QPointF(x + 0.6 * self.string_height, y - 0.4 * self.string_height),
        )
        if note.base_duration() in (192, 384):
          ctx.setBrush(qtcore.Qt.white)
          ctx.drawPolygon(
            qtcore.QPointF(x + 0.3 * self.string_height, y),
            qtcore.QPointF(x + 0.6 * self.string_height, y + 0.3 * self.string_height),
            qtcore.QPointF(x + 0.9 * self.string_height, y),
            qtcore.QPointF(x + 0.6 * self.string_height, y - 0.3 * self.string_height),
          )
          
    elif note.fx != "dead":
      if note.duration_fx == "appoggiatura": # White appoggiatura should never exist !
        ctx_drawEllipse(ctx,
          x + 0.35 * self.string_height,
          y - 0.25 * self.string_height + 0.5,
              0.5  * self.string_height,
              0.5  * self.string_height,
        )
      else:
        ctx_drawEllipse(ctx,
          x + 0.2 * self.string_height,
          y - 0.4 * self.string_height + 0.5,
              0.8 * self.string_height,
              0.8 * self.string_height,
        )
        if note.base_duration() in (192, 384): # White notes:
          ctx.setBrush(qtcore.Qt.white)
          ctx_drawEllipse(ctx, 
            x + 0.3 * self.string_height,
            y - 0.3 * self.string_height + 0.5,
                0.6 * self.string_height,
                0.6 * self.string_height,
          )
    ctx.restore()
    
    if note.base_duration() in (192, 384):
      line_y = self.string_id_2_y(string_id)
      self._draw_perfect_line(ctx, x + 0.2 * self.string_height, line_y, x + self.string_height, line_y)
      
    alteration = abs(note.value) - string.base_note
    if alteration > 6: alteration -= 12
    
    previous = self.note_previous(note)
    if previous and (self.partition.song.mesure_at(previous) is self.partition.song.mesure_at(note)):
      previous_alteration = abs(previous.value) - string.base_note
      if previous_alteration > 6: previous_alteration -= 12
    else: previous_alteration = 0
    
    if alteration != previous_alteration:
      if   alteration == -2: t = "♭♭"
      elif alteration == -1: t = "♭"
      elif alteration ==  0: t = "♮"
      elif alteration ==  1: t = "♯"
      elif alteration ==  2: t = "♯♯"
      else:                  t = "?"
      ctx_drawText(ctx, x - self.canvas.char_h_size * 0.5, y + self.canvas.default_ascent // 2 - 1, t)
      
    if note.is_dotted():
      ctx_drawEllipse(ctx, x + 1.3 * self.string_height, y - 0.5   * self.string_height, 3 * self.scale, 3 * self.scale)
      
    if note.fx     : getattr(self, "draw_note_fx_%s" % note.fx     )(ctx, note, string_id)
    if note.link_fx: getattr(self, "draw_note_fx_%s" % note.link_fx)(ctx, note, string_id)
    
  def note_width(self, note): return self.string_height
  
  on_touchscreen_new_note = canvas_module.PartitionDrawer.on_touchscreen_new_note
  
  def note_value_possible(self, note, value):
    for i, string in enumerate(self.strings): # Search a string with the right tone
      if ((string.base_note % 12) == (value % 12)): return 1
    return 0
  
  def note_string_id(self, note): return self.partition.view.note_string_id(note)
  
  def draw_stem_and_beam_for_chord(self, ctx, notes, notes_y, previous, next, appo = 0):
    if not appo:
      canvas_module.TablatureDrawer.draw_stem_and_beam_for_chord(self, ctx, notes, notes_y, previous, next, 0)
      
  _drawers                        = canvas_module.PartitionDrawer._drawers.copy()
  _drawers[288] = _drawers[192]   = canvas_module.PartitionDrawer._black
  _drawers8                       = canvas_module.PartitionDrawer._drawers8.copy()
  _drawers8[288] = _drawers8[192] = canvas_module.PartitionDrawer._black
  
  draw_note_fx_link = canvas_module.PartitionDrawer.draw_note_fx_link # No "p" / "h" for pull / hammer
  
  def draw(self, ctx, x, y, width, height, drag = 0):
    canvas_module.TablatureDrawer.draw(self, ctx, x, y, width, height, drag)
    if not drag:
      ctx.setFont(self.canvas.small_font)
      for i in range(len(self.strings)):
        label = model.note_label(self.strings[i].base_note, 0, self.partition.tonality)
        ctx_drawText(ctx, self.canvas.start_x - 2.2 * self.canvas.char_h_size, self.string_id_2_y(i) + self.canvas.small_ascent * 0.3, label)
      ctx.setFont(self.canvas.default_font)
      
    
