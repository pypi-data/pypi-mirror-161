# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2008 Jean-Baptiste LAMY -- jibalamy@free.fr
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

import editobj3, editobj3.introsp as introsp, editobj3.field as field
import songwrite3.model   as model
import songwrite3.plugins as plugins

class FingeringView(model.View):
  view_class               = "fingering"
  default_instrument       = 72
  default_icon_filename    = "flute.png"
  
  def __init__(self, partition, name = ""):
    model.View.__init__(self, partition, name)
    if not hasattr(partition, "print_with_staff_too"): partition.print_with_staff_too = 0
    
  def get_drawer(self, canvas, compact = False):
    from songwrite3.plugins.fingering.drawer import FingeringDrawer, SingleString
    return FingeringDrawer(canvas, self.partition, compact, SingleString)

  def get_type(self):
    return self.__class__
  
  def note_2_fingering(self, note):
    v = abs(note.value)
    if getattr(self.partition, "g8", 0): v += 12
    return self.fingerings.get(v)
  

class TinWhistleView(FingeringView):
  default_instrument    = 72
  default_icon_filename = "flute_irlandaise.png"
  fingerings = {
    #note : (hole1, hole2, hole3, hole4, hole5, hole6,   breath),
    62 : (1  , 1  , 1  , None, 1  , 1  , 1  ,     ""),
    63 : (1  , 1  , 1  , None, 1  , 1  , 0.5,     ""),
    64 : (1  , 1  , 1  , None, 1  , 1  , 0  ,     ""),
    65 : (1  , 1  , 1  , None, 1  , 0.5, 0  ,     ""),
    66 : (1  , 1  , 1  , None, 1  , 0  , 0  ,     ""),
    67 : (1  , 1  , 1  , None, 0  , 0  , 0  ,     ""),
    68 : (1  , 1  , 0.5, None, 0  , 0  , 0  ,     ""),
    69 : (1  , 1  , 0  , None, 0  , 0  , 0  ,     ""),
    70 : (1  , 0.5, 0  , None, 0  , 0  , 0  ,     ""),
    71 : (1  , 0  , 0  , None, 0  , 0  , 0  ,     ""),
    72 : (0  , 1  , 1  , None, 1  , 0  , 1  ,     ""),
    73 : (0  , 0  , 0  , None, 0  , 0  , 0  ,     ""),
    
    74 : (0  , 1  , 1  , None, 1  , 1  , 1  ,     "+"),
    75 : (1  , 1  , 1  , None, 1  , 1  , 0.5,     "+"),
    76 : (1  , 1  , 1  , None, 1  , 1  , 0  ,     "+"),
    77 : (1  , 1  , 1  , None, 1  , 0.5, 0  ,     "+"),
    78 : (1  , 1  , 1  , None, 1  , 0  , 0  ,     "+"),
    79 : (1  , 1  , 1  , None, 0  , 0  , 0  ,     "+"),
    80 : (1  , 1  , 0.5, None, 0  , 0  , 0  ,     "+"),
    81 : (1  , 1  , 0  , None, 0  , 0  , 0  ,     "+"),
    82 : (1  , 0.5, 0  , None, 0  , 0  , 0  ,     "+"),
    83 : (1  , 0  , 0  , None, 0  , 0  , 0  ,     "+"),
    85 : (0  , 0  , 0  , None, 0  , 0  , 0  ,     "+"),
    }
  
  def __init__(self, partition, name = ""):
    if not hasattr(partition, "instrument_tonality"):
      partition.instrument_tonality = "D"
      if not partition.notes: partition.tonality = "D"
    FingeringView.__init__(self, partition, name or _("Tin whistle"))
    
  def get_icon_filename(self): return "flute_irlandaise.png"
  
  def note_2_fingering(self, note):
    v = abs(note.value)
    if getattr(self.partition, "g8", 0): v += 12
    return self.fingerings.get(v - model.OFFSETS[self.partition.instrument_tonality] + 2)
  
  def get_bell_note(self):
    bell_note = 62 + model.OFFSETS[self.partition.instrument_tonality] - 2
    if self.partition.g8: bell_note -= 12
    return bell_note
  
  def get_drawer(self, canvas, compact = False):
    from songwrite3.plugins.fingering.drawer import FingeringDrawer, TinWhistleSingleString
    return FingeringDrawer(canvas, self.partition, compact, TinWhistleSingleString)
  
  def __xml__(self, xml = None, context = None):
    xml.write(u'''\t\t<view type="tin_whistle"/>\n''')
    
    
class RecorderView(FingeringView):
  default_instrument = 73
  fingerings = {
    #note : (hole1, hole2, hole3, hole4, hole5, hole6,   breath),
    60 : (1  , None, 1  , 1  , 1  , None, 1  , 1  , (1, 1), (1, 1),    ""),
    61 : (1  , None, 1  , 1  , 1  , None, 1  , 1  , (1, 1), (1, 0),    ""),
    62 : (1  , None, 1  , 1  , 1  , None, 1  , 1  , (1, 1), (0, 0),    ""),
    63 : (1  , None, 1  , 1  , 1  , None, 1  , 1  , (1, 0), (0, 0),    ""),
    64 : (1  , None, 1  , 1  , 1  , None, 1  , 1  , (0, 0), (0, 0),    ""),
    65 : (1  , None, 1  , 1  , 1  , None, 1  , 0  , (1, 1), (1, 1),    ""),
    66 : (1  , None, 1  , 1  , 1  , None, 0  , 1  , (1, 1), (0, 0),    ""),
    67 : (1  , None, 1  , 1  , 1  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    68 : (1  , None, 1  , 1  , 0  , None, 1  , 1  , (0, 0), (0, 0),    ""),
    69 : (1  , None, 1  , 1  , 0  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    70 : (1  , None, 1  , 0  , 1  , None, 1  , 0  , (0, 0), (0, 0),    ""),
    71 : (1  , None, 1  , 0  , 0  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    
    72 : (1  , None, 0  , 1  , 0  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    73 : (0  , None, 1  , 1  , 0  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    74 : (0  , None, 0  , 1  , 0  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    75 : (0  , None, 1  , 1  , 1  , None, 1  , 1  , (1, 1), (1, 1),    ""),
    76 : (0.5, None, 1  , 1  , 1  , None, 1  , 1  , (0, 0), (0, 0),    ""),
    77 : (0.5, None, 1  , 1  , 1  , None, 1  , 0  , (1, 1), (0, 0),    ""),
    78 : (0.5, None, 1  , 1  , 1  , None, 0  , 1  , (0, 0), (0, 0),    ""),
    79 : (0.5, None, 1  , 1  , 1  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    80 : (0.5, None, 1  , 1  , 0  , None, 1  , 0  , (0, 0), (0, 0),    ""),
    81 : (0.5, None, 1  , 1  , 0  , None, 0  , 0  , (0, 0), (0, 0),    ""),
    82 : (0.5, None, 1  , 1  , 0  , None, 1  , 1  , (1, 1), (0, 0),    ""),
    83 : (0.5, None, 1  , 1  , 0  , None, 1  , 1  , (0, 0), (0, 0),    ""),
    
    84 : (0.5, None, 1  , 0  , 0  , None, 1  , 1  , (0, 0), (0, 0),    ""),
    85 : (0.5, None, 1  , 0  , 1  , None, 1  , 0  , (0, 0), (0, 0),    ""),
    86 : (0.5, None, 1  , 0  , 1  , None, 1  , 0  , (1, 1), (0, 0),    ""),
    87 : (0.5, None, 0  , 1  , 1  , None, 0  , 1  , (1, 1), (0, 0),    ""),
    }
  
  def __init__(self, partition, name = ""):
    FingeringView.__init__(self, partition, name or _("Recorder"))
    
  def get_icon_filename(self): return "flute.png"
  
  def get_bell_note(self):
    bell_note = 60
    if self.partition.g8: bell_note -= 12
    return bell_note
  
  
  def __xml__(self, xml = None, context = None):
    xml.write(u'''\t\t<view type="recorder"/>''')
    
  
model.VIEW_CATEGORIES.append("fingering")
plugins.ViewPlugin(TinWhistleView, None, "tin_whistle", "fingering")
plugins.ViewPlugin(RecorderView  , None, "recorder"   , "fingering")

#descr = introsp.description(model.Partition)
#descr.set_field_for_attr("instrument_tonality"  , field.EnumField(dict([(_("tonality_%s" % tonality), tonality) for tonality in model.TONALITIES.keys()])))


