# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2009-2016 Jean-Baptiste LAMY -- jibalamy@free.fr
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

import songwrite3.model   as model
import songwrite3.plugins as plugins

class LyreView(model.TablatureView):
  view_class               = "lyre_tablature"
  default_instrument       = 46
  default_icon_filename    = "lyre.png"
  link_type                = model.LINK_NOTES_DEFAULT
  automatic_string_id      = 1
  use_harmonics_for_octavo = 1
  
  def __init__(self, partition, name = "", strings = None):
    if partition:
      if not hasattr(partition, "let_ring"): partition.let_ring = 1
    model.TablatureView.__init__(self, partition, name, strings)
    self.tonality = "C"
    self.set_tonality(partition.tonality)
    
  def note_string_id(self, note):
    return self._calc_string_id(note.value)
  
  def _calc_string_id(self, value):
    value = abs(value)
    for i, string in enumerate(self.strings): # Search an exact match
      if string.base_note == value: return i
      
    value2 = value % 12
    for i, string in enumerate(self.strings): # Search a string with the right tone
      if (string.base_note % 12) == value2: return i
      
    for i, string in enumerate(self.strings): # Search a string with a #
      if string.base_note == value - 1: return i
      
    for i, string in enumerate(self.strings): # Search a string with the right tone and a #
      if (string.base_note % 12) == value2 - 1: return i
    return len(self.strings) - 1
  
  def get_drawer(self, canvas, compact = False):
    from songwrite3.plugins.lyre.drawer import LyreDrawer
    return LyreDrawer(canvas, self.partition, compact)
  
  def get_icon_filename(self): return "lyre.png"
  
  def get_type(self):
    if   len(self.strings) == 6: return model.TablatureView.get_type(self, SixStringLyreView)
    else:                        return model.TablatureView.get_type(self, SevenStringLyreView)
    
  def set_tonality(self, tonality):
    # Remove previous tonality first
    alterations = model.TONALITIES[self.tonality]
    if alterations:
      if alterations[0] == model.DIESES[0]: alteration_type =  1 # diese
      else:                                 alteration_type = -1 # bemol
    else:                                   alteration_type =  0
    
    for string in self.strings:
      for alteration in alterations:
        if (string.base_note % 12) - alteration_type == alteration:
          string.base_note -= alteration_type
          break
        
    self.tonality = tonality
    
    alterations = model.TONALITIES[tonality]
    if alterations:
      if alterations[0] == model.DIESES[0]: alteration_type =  1 # diese
      else:                                 alteration_type = -1 # bemol
    else:                                   alteration_type =  0
    
    for string in self.strings:
      for alteration in alterations:
        if (string.base_note % 12) == alteration:
          string.base_note += alteration_type
          break
        
  def __xml__(self, xml = None, context = None): model.TablatureView.__xml__(self, xml, context, type = "lyre")


_LYRE_STRING_COLORS = [
  "red"  , #  0
  "red"  , #  1
  "black", #  2
  "black", #  3
  "black", #  4
  "blue" , #  5
  "blue" , #  6
  "black", #  7
  "black", #  8
  "black", #  9
  "black", # 10
  "black", # 11
  ]
class LyreString(model.TablatureString):
  def color(self): return _LYRE_STRING_COLORS[self.base_note % 12]
model.LyreString = LyreString

class SixStringLyreView(LyreView):
  def __init__(self, partition, name = ""):
    super(SixStringLyreView, self).__init__(partition, name or _("Lyre"), self.new_strings())
  @classmethod
  def new_strings(Class):
    return[LyreString(64, -1), LyreString(62, -1), LyreString(60, -1), LyreString(59, -1), LyreString(57, -1), LyreString(55, -1)]
  
class SevenStringLyreView(LyreView):
  def __init__(self, partition, name = ""):
    super(SevenStringLyreView, self).__init__(partition, name or _("Lyre"), self.new_strings())
  @classmethod
  def new_strings(Class):
    return[LyreString(64, -1), LyreString(62, -1), LyreString(60, -1), LyreString(59, -1), LyreString(57, -1), LyreString(55, -1), LyreString(53, -1)]
  

  
plugins.ViewPlugin(LyreView           , LyreString, "lyre"             , None)
plugins.ViewPlugin(SixStringLyreView  , LyreString, "six_string_lyre"  , "tab")
plugins.ViewPlugin(SevenStringLyreView, LyreString, "seven_string_lyre", "tab")
