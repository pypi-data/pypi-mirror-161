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

import sys, os, os.path

import songwrite3.globdef as globdef
import songwrite3.model   as model

PLUGINS = {}
class Plugin(object):
  def __init__(self, name):
    print("Registering %s plugin..." % name, file = sys.stderr)
    
    self.name = name
    
    PLUGINS[name] = self
    
  def create_ui(self, app):
    pass


EXPORT_FORMATS = []
class ExportPlugin(Plugin):
  def __init__(self, format, exts, can_export_song = 1, can_export_songbook = 0):
    self.format              = format
    self.exts                = exts
    self.can_export_song     = can_export_song
    self.can_export_songbook = can_export_songbook
    EXPORT_FORMATS.append(format)
    Plugin.__init__(self, "%s exporter" % format.lower())
    
  def create_ui(self, app):
    if self.can_export_song:
      app.add_to_menu(app.export_menu, 0, _("Export to %s") % self.format + "..." * int(globdef.config.ASK_FILENAME_ON_EXPORT), self.on_menu_click, arg = app)
    if self.can_export_songbook:
      app.add_to_menu(app.export_songbook_menu, 0, _("Export songbook to %s") % self.format + "..." * int(globdef.config.ASK_FILENAME_ON_EXPORT), self.on_songbook_menu_click, arg = app)
      
  def on_menu_click(self, widget, app):
    if globdef.config.ASK_FILENAME_ON_EXPORT or (not app.filename):
      filename = app.prompt_save_filename(self.exts, self.format)
    else:
      filename = app.filename.replace(".sw.xml", "") + "." + self.exts[0]
    if filename: self.export_to(app.song, filename)
    
  def on_songbook_menu_click(self, widget, app):
    if globdef.config.ASK_FILENAME_ON_EXPORT or (not app.songbook.filename):
      filename = app.prompt_save_filename(self.exts, self.format)
    else:
      filename = app.songbook.filename.replace(".sw.xml", "") + "." + self.exts[0]
    if filename: self.export_to(app.songbook, filename)
    
  def export_to(self, song, filename):
    data = self.export_to_string(song)
    if isinstance(data, bytes):
      if filename == "-": sys.stdout.buffer.write(data)
      else: open(filename, "wb").write(data)
    else:
      if filename == "-": print(data)
      else: open(filename, "w").write(data)
      
  def export_to_string(self, song): pass
  
  
IMPORT_FORMATS = []
class ImportPlugin(Plugin):
  def __init__(self, format, exts, binary = False):
    self.format = format
    self.exts   = exts
    self.binary = binary
    IMPORT_FORMATS.append(format)
    Plugin.__init__(self, "%s importer" % format.lower())
    
  def create_ui(self, app):
    app.add_to_menu(app.import_menu, 0, _("Import from %s") % self.format + "...", self.on_menu_click, arg = app)
    
  def on_menu_click(self, widget, app):
    if app.check_save(): return
    
    filename = app.prompt_open_filename(self.exts, self.format)
    
    if filename:
      song = self.import_from(filename)
      app.set_song(song)
      
  def import_from(self, filename):
    if filename == "-":
      return self.import_from_string(sys.stdin.read())
    else:
      if self.binary: s = open(filename, "rb").read()
      else:           s = open(filename      ).read()
    return self.import_from_string(s)
    
  def import_from_string(self, data): pass


PLUGINS_VIEWS = {}
class ViewPlugin(Plugin):
  def __init__(self, View, String, code_name, category):
    PLUGINS_VIEWS[code_name] = View, String
    Plugin.__init__(self, "%s view" % code_name)
    
    if category: model.VIEWS[category].append(View)
    
    
def create_plugins_ui(app):
  for plugin in PLUGINS.values(): plugin.create_ui(app)
  
def load_all_plugins():
  plugins_dir = os.path.dirname(__file__)
  for file in [
    "songwrite",
    "abc",
    "texttab",
    "midi",
    "pdf",
    "fingering",
    "additional_instruments",
    "lyre",
    "chord",
    "accordion",
    ]:
    try:
      __import__("songwrite3.plugins.%s" % file)
    except:
      print("Error while loading plugin 'songwrite3.plugins.%s'!" % file, file = sys.stderr)
      sys.excepthook(*sys.exc_info())
  print(file = sys.stderr)
  
def get_importer(format):
  return PLUGINS["%s importer" % format.lower()]

def get_exporter(format):
  return PLUGINS["%s exporter" % format.lower()]

def load_view(partition, attrs):
  View, String = PLUGINS_VIEWS[attrs["type"]]
  view = View(partition, "")
  view.load_attrs(attrs)
  return view, String
  
