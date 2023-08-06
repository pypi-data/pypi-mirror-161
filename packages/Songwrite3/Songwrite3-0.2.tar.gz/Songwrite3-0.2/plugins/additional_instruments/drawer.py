# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2012 Jean-Baptiste LAMY -- jibalamy@free.fr
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

import songwrite3.canvas as canvas



class LuteDrawer(canvas.TablatureDrawer):
  def __init__(self, canvas_, partition, compact = False):
    canvas.TablatureDrawer.__init__(self, canvas_, partition, compact)
    
  def on_key_press(self, event):
    keyval = event.key()
    if   qtcore.Qt.Key_A <= keyval <= qtcore.Qt.Key_N: # a-n
      self.canvas.on_number_typed(str(keyval - qtcore.Qt.Key_A))
      return 1

