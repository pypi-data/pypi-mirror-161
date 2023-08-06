# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2007-2011 Jean-Baptiste LAMY -- jibalamy@free.fr
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

plugins.Plugin("additional_instruments")

class Banjo5GTablatureString(model.TablatureString):
  def value_2_text(self, note):
    if note.value == self.base_note: return "0"
    return unicode(note.value - self.base_note - note.partition.capo + 5)
  
  def text_2_value(self, note, text):
    text = int(text)
    if text <= 5: return self.base_note + note.partition.capo
    return text + self.base_note + note.partition.capo - 5
  
model.Banjo5GTablatureString = Banjo5GTablatureString

class Banjo5GView(model.TablatureView):
  default_instrument = 105
  def __init__(self, partition, name = ""):
    super(Banjo5GView, self).__init__(partition, name or _("Banjo 5G"), self.new_strings())
  @classmethod
  def new_strings(Class):
    return [model.TablatureString(62, -1), model.TablatureString(59, -1), model.TablatureString(55, -1), model.TablatureString(50, -1), Banjo5GTablatureString(67, -1)]
model.VIEWS["tab"].append(Banjo5GView)

class UkuleleView(model.TablatureView):
  default_instrument = 27
  def __init__(self, partition, name = ""):
    super(UkuleleView, self).__init__(partition, name or _("Ukulele"), self.new_strings())
  @classmethod
  def new_strings(Class):
    return [model.TablatureString(69, -1), model.TablatureString(64, -1), model.TablatureString(60, -1), model.TablatureString(55, -1)]
model.VIEWS["tab"].append(UkuleleView)

class MandolinView(model.TablatureView):
  default_instrument = 105
  def __init__(self, partition, name = ""):
    super(MandolinView, self).__init__(partition, name or _("Mandolin"), self.new_strings())
  @classmethod
  def new_strings(Class):
    return [model.TablatureString(76, -1), model.TablatureString(69, -1), model.TablatureString(62, -1), model.TablatureString(55, -1)]
model.VIEWS["tab"].append(MandolinView)

class KoyabuView(model.TablatureView):
  default_instrument = 27
  def __init__(self, partition, name = ""):
    super(KoyabuView, self).__init__(partition, name or _("Koyabu board"), self.new_strings())
  @classmethod
  def new_strings(Class):
    return [
    model.TablatureString(24, -1),
    model.TablatureString(31, -1),
    model.TablatureString(38, -1),
    model.TablatureString(45, -1),
    model.TablatureString(52, -1),
    model.TablatureString(59, -1),
    model.TablatureString(64, -1),
    model.TablatureString(57, -1),
    model.TablatureString(52, -1),
    model.TablatureString(47, -1),
    model.TablatureString(42, -1),
    model.TablatureString(37, -1),
    ]
model.VIEWS["tab"].append(KoyabuView)


class LuteView(model.TablatureView):
  default_instrument = 27
  def __init__(self, partition, name = ""):
    super(LuteView, self).__init__(partition, name or _("Lute"), self.new_strings())
  @classmethod
  def new_strings(Class):
    return [model.LuteTablatureString(69, -1),
            model.LuteTablatureString(64, -1),
            model.LuteTablatureString(60, -1),
            model.LuteTablatureString(55, -1)]

  def get_drawer(self, canvas, compact = False):
    from songwrite3.plugins.additional_instruments.drawer import LuteDrawer
    return LuteDrawer(canvas, self.partition, compact)

model.VIEWS["tab"].append(LuteView)

class LuteTablatureString(model.TablatureString):
  def value_2_text(self, note):
    if note.value == self.base_note: return "a"
    return chr(note.value - self.base_note - note.partition.capo + 97)
  
model.LuteTablatureString = LuteTablatureString
