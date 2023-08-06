# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2007 Jean-Baptiste LAMY -- jibalamy@free.fr
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


class ExportPlugin(plugins.ExportPlugin):
  def __init__(self):
    plugins.ExportPlugin.__init__(self, "TextTab", [".txt"], 1, 1)
    
  def export_to_string(self, song):
    import songwrite3.plugins.texttab.texttab as texttab
    if isinstance(song, model.Songbook):
      return "\n\n\n\n".join(texttab.texttab(song_ref.get_song()) for song_ref in song.song_refs)
    else:
      return texttab.texttab(song)
    
ExportPlugin()

class ImportPlugin(plugins.ImportPlugin):
  def __init__(self):
    plugins.ImportPlugin.__init__(self, "TextTab", [".txt"])
    
  def import_from(self, filename):
    import songwrite3.plugins.texttab.texttab as texttab
    return texttab.parse(open(filename).read())
  
ImportPlugin()
