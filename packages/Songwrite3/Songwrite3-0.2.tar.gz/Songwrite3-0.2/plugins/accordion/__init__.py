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

import editobj3, editobj3.introsp as introsp, editobj3.field as field
import songwrite3.model   as model
import songwrite3.plugins as plugins

#model.Note.accompaniment = None
model.Note.button_rank   = None
model.Note.bellows_dir   = None # -1 Push, 1 draw
model.NOTE_ATTRS.append("button_rank")
model.NOTE_ATTRS.append("bellows_dir")

accordion_tonalities = {
  -5 : _("C/F"),
   0 : _("G/C"),
   2 : _("A/D"),
  }

class AccordionView(model.View):
  view_class               = "accordion"
  default_icon_filename    = "accordion.png"
  default_instrument       = 21
  link_type                = model.LINK_NOTES_DEFAULT
  can_paste_note_by_string = 1
  automatic_string_id      = 1
  def __init__(self, partition, name = ""):
    model.View.__init__(self, partition, name or _("Accordion"))
    if partition:
      if not hasattr(partition, "print_with_staff_too"): partition.print_with_staff_too = 0
      if not hasattr(partition, "accordion_tonalities"): partition.accordion_tonalities = 0
    self.strings = [
      AccordionLeftHandString (self, -1, { "1" : 51, "2" : 50, "3" : 55, "4" : 59, "5" : 62, "6" : 67, "7" : 71, "8" : 74, "9" : 79, "10" : 83, "11" : 86,
                                           "1'": 56, "2'": 55, "3'": 60, "4'": 64, "5'": 67, "6'": 72, "7'": 76, "8'": 79, "9'": 84, "10'": 88 }), # Poussé
      AccordionLeftHandString (self,  1, { "1" : 49, "2" : 54, "3" : 57, "4" : 60, "5" : 64, "6" : 66, "7" : 69, "8" : 72, "9" : 76, "10" : 78, "11" : 81,
                                           "1'": 48, "2'": 59, "3'": 62, "4'": 65, "5'": 69, "6'": 71, "7'": 74, "8'": 77, "9'": 81, "10'": 83}), # Tiré
      ]
  
  def note_string_id(self, note):
    if   note.bellows_dir == -1: return 0
    elif note.bellows_dir ==  1: return 1
    return 1
  
  def get_drawer(self, canvas, compact = False):
    from songwrite3.plugins.accordion.drawer import AccordionDrawer
    return AccordionDrawer(canvas, self.partition, compact)
  
  def get_icon_filename(self): return "accordion.png"
  
  def __xml__(self, xml = None, context = None):
    xml.write('''\t\t<view type="accordion">\n''')
    xml.write("""\t\t</view>\n""")
    

#class AccordionLeftHandString(object):
class AccordionLeftHandString(model.TablatureString):
  def __init__(self, view, bellows_dir, button2value):
    self.view          = view
    self.bellows_dir   = bellows_dir
    self.button2value  = button2value
    self.value2buttons = {}
    # First pass for button rank 0, then second pass for button rank 1
    for button, value in button2value.items():
      if not "'" in button:
        if value in self.value2buttons: self.value2buttons[value].append(button)
        else:                           self.value2buttons[value] = [button]
    for button, value in button2value.items():
      if "'" in button:
        if value in self.value2buttons: self.value2buttons[value].append(button)
        else:                           self.value2buttons[value] = [button]
    self.base_note = self.button2value["3"]
    
  def text_2_value(self, note, text):
    value = self.button2value.get(text)
    if value is None:
      if len(text) > 1:
        value = self.button2value.get(text[-1])
      if value is None: 
        value = self.button2value["3"]
    note.button_rank = text.count("'")
    note.bellows_dir = self.bellows_dir
    return value
  def value_2_text(self, note, change_string = 1):
    buttons = self.value2buttons.get(note.value)
    if buttons is None:
      if change_string:
        for string in self.view.strings:
          if string is self: continue
          text = string.value_2_text(note, change_string = 0)
          if text:
            note.bellows_dir = string.bellows_dir
            return text
      return "?"
    if len(buttons) == 1: return buttons[0]
    button_rank = note.button_rank
    if button_rank is None:
      if (note.partition.tonality == "G") or (note.partition.tonality == "D"): button_rank = 0
      else:                                                                    button_rank = 1
    return buttons[button_rank]
  
  def width(self): return 7
  
  #def __str__(self): return _(self.__class__.__name__) % model.note_label(self.base_note)

#descr = introsp.description(AccordionLeftHandString)
introsp.def_attr("bellows_dir", field.HiddenField)

plugins.ViewPlugin(AccordionView, None, "accordion", "tab")
