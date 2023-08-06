# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2001-2016 Jean-Baptiste LAMY -- jibalamy@free.fr
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

import sys, time, getpass, os, os.path, locale, unicodedata, subprocess
from io import StringIO

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui

import editobj3, editobj3.undoredo as undoredo, editobj3.introsp as introsp, editobj3.field as field, editobj3.editor as editor, editobj3.editor_qt as editor_qt
from editobj3.observe import *

import songwrite3, songwrite3.globdef as globdef, songwrite3.model as model, songwrite3.player as player
import songwrite3.__editobj3__
import songwrite3.midi

editor_qt.MENU_LABEL_2_IMAGE.update({
  "Open..."                            : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-open.svg")),
  "Save"                               : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-save.svg")),
  "Save as..."                         : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-save.svg")),
  "Close"                              : qtgui.QIcon(os.path.join(globdef.DATADIR, "window-close.svg")),
  "Undo"                               : qtgui.QIcon(os.path.join(globdef.DATADIR, "edit-undo.svg")),
  "Redo"                               : qtgui.QIcon(os.path.join(globdef.DATADIR, "edit-redo.svg")),
  "Paste"                              : qtgui.QIcon(os.path.join(globdef.DATADIR, "edit-paste.svg")),
  "Preferences..."                     : qtgui.QIcon(os.path.join(globdef.DATADIR, "preferences-desktop.svg")),
  
  "Add..."                             : qtgui.QIcon(os.path.join(globdef.DATADIR, "list-add.svg")),
  "Remove"                             : qtgui.QIcon(os.path.join(globdef.DATADIR, "list-remove.svg")),
  "Move up"                            : qtgui.QIcon(os.path.join(globdef.DATADIR, "go-up.svg")),
  "Move down"                          : qtgui.QIcon(os.path.join(globdef.DATADIR, "go-down.svg")),
  "Play from the beginning"            : qtgui.QIcon(os.path.join(globdef.DATADIR, "media-playback-start.svg")),
  "Play from the beginning in loop"    : qtgui.QIcon(os.path.join(globdef.DATADIR, "media-playback-start.svg")),
  "Play from here"                     : qtgui.QIcon(os.path.join(globdef.DATADIR, "media-playback-start.svg")),
  "Play from here in loop"             : qtgui.QIcon(os.path.join(globdef.DATADIR, "media-playback-start.svg")),
  "Stop playing"                       : qtgui.QIcon(os.path.join(globdef.DATADIR, "media-playback-stop.svg")),
  "Edit..."                            : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-properties.svg")),
  "Songbook properties..."             : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-properties.svg")),
  "Song and instruments properties..." : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-properties.svg")),
  "Instrument properties..."           : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-properties.svg")),
  "Note properties..."                 : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-properties.svg")),
  "Save songbook as..."                : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-save.svg")),
  "preview_print"                      : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-print.svg")),
  "preview_print_songbook"             : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-print.svg")),
  "New window..."                      : qtgui.QIcon(os.path.join(globdef.DATADIR, "window-new.svg")),
  "New song"                           : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-new.svg")),
  "New songbook"                       : qtgui.QIcon(os.path.join(globdef.DATADIR, "document-new.svg")),
  "Select all"                         : qtgui.QIcon(os.path.join(globdef.DATADIR, "edit-select-all.svg")),
  "Paste last selection"               : qtgui.QIcon(os.path.join(globdef.DATADIR, "edit-paste.svg")),
  "About..."                           : qtgui.QIcon(os.path.join(globdef.DATADIR, "help-about.svg")),
  "Manual..."                          : qtgui.QIcon(os.path.join(globdef.DATADIR, "help-contents.svg")),
  })

from songwrite3.canvas import Canvas

app      = qtwidgets.QApplication(sys.argv)
mainloop = app.exec
app.setWindowIcon(qtgui.QIcon(os.path.join(globdef.DATADIR, "songwrite3_64x64.png")))



# try:
#   s = open(os.path.expanduser("~/.config/qt5ct/qt5ct.conf")).read()
#   s = s.split("style=", 1)[1].split("\n", 1)[0]
#   app.setStyle(s)
#   del s
# except: pass

#if hasattr(qtcore.Qt, 'AA_EnableHighDpiScaling'): app.setAttribute(qtcore.Qt.AA_EnableHighDpiScaling, True)
#if hasattr(qtcore.Qt, 'AA_UseHighDpiPixmaps'):    app.setAttribute(qtcore.Qt.AA_UseHighDpiPixmaps   , True)
    
def remove_accents(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


APPS = {}

class App(editor_qt.QtBaseDialog):
  def __init__(self, song = None):
    self.init_window(False)
    
    self.undo_stack       = undoredo.Stack(globdef.config.NUMBER_OF_UNDO)
    self.updating_menu    = False
    self.partition_editor = None
    self.mesure_editor    = None
    self.note_editor      = None
    self.filename         = None
    
    self.build_default_menubar()
    
    #file_menu = self.add_to_menu(self.menubar, 1, "File", self.on_file_menu)
    file_menu = self.file_menu
    self.add_to_menu(file_menu, 0, "New window..."      , self.on_new_app     , pos = 0)
    self.add_to_menu(file_menu, 0, "New song"           , self.on_new         , pos = 1, accel = "C-N")
    self.add_to_menu(file_menu, 0, "New songbook"       , self.on_new_songbook, pos = 2)
    self.add_to_menu(file_menu, 0, "Open..."            , self.on_open        , pos = 3, accel = "C-O")
    self.add_to_menu(file_menu, 0, "Save"               , self.on_save        , pos = 4, accel = "C-S")
    self.add_to_menu(file_menu, 0, "Save as..."         , self.on_save_as     , pos = 5, accel = "C-S-S")
    self.save_as_songbook_menu = self.add_to_menu(file_menu, 0, "Save songbook as...", self.on_save_as_songbook, pos = 6)
    self.add_separator_to_menu(file_menu, pos = 7)
    
    self.import_menu          = self.add_to_menu(file_menu, 1, "Import", pos = 8)
    self.export_menu          = self.add_to_menu(file_menu, 1, "Export", pos = 9)
    self.export_songbook_menu = self.add_to_menu(file_menu, 1, "Export songbook", pos = 10)
    
    self.add_to_menu(file_menu, 0, "preview_print", self.on_preview_print, pos = 11)
    self.preview_print_songbook_menu = self.add_to_menu(file_menu, 0, "preview_print_songbook", self.on_preview_print_songbook, pos = 12)
    self.add_separator_to_menu(file_menu, pos = 13)
    #self.add_to_menu(file_menu, 0, "Close", self.on_close)
    
    self.add_separator_to_menu(file_menu)
    for file in globdef.config.PREVIOUS_FILES:
      self.add_to_menu(file_menu, 0, file, lambda obj, file = file: self.open_filename(file))
      
    #edit_menu = self.add_to_menu(self.menubar, 1, "Edit", self.on_edit_menu)
    edit_menu = self.edit_menu
    #self.undo_menu = self.add_to_menu(edit_menu, 0, "Undo", self.on_undo, accel = "C-Z")
    #self.redo_menu = self.add_to_menu(edit_menu, 0, "Redo", self.on_redo, accel = "C-Y")
    self.add_separator_to_menu(edit_menu)
    self.add_to_menu(edit_menu, 0, "Select all"              , self.on_select_all, accel = "C-A", accel_enabled = 0) # Disabled these accels,
    self.add_to_menu(edit_menu, 0, "Cut"                     , self.on_note_cut  , accel = "C-X", accel_enabled = 0) # because they block C-A, C-V,... in lyrics editor
    self.add_to_menu(edit_menu, 0, "Copy"                    , self.on_note_copy , accel = "C-C", accel_enabled = 0)
    self.add_to_menu(edit_menu, 0, "Paste"                   , self.on_note_paste, accel = "C-V", accel_enabled = 0)
    self.add_to_menu(edit_menu, 0, "Insert/remove beats..."  , self.on_insert_times)
    self.add_to_menu(edit_menu, 0, "Insert/remove bars..."   , self.on_insert_bars)
    self.add_separator_to_menu(edit_menu)
    self.add_to_menu(edit_menu, 0, "Rhythm and bars..."     , self.on_bars_prop)
    self.add_to_menu(edit_menu, 0, "Repeats and playlist...", self.on_playlist_prop)
    self.add_separator_to_menu(edit_menu)
    self.add_to_menu(edit_menu, 0, "Preferences...", self.on_preferences)
    
    play_menu = self.add_to_menu(self.menubar, 1, "Play")
    self.add_to_menu(play_menu, 0, "Play from the beginning"        , self.on_play)
    self.add_to_menu(play_menu, 0, "Play from here"                 , self.on_play_from_here, accel = " ")
    self.add_to_menu(play_menu, 0, "Play from the beginning in loop", self.on_play_in_loop)
    self.add_to_menu(play_menu, 0, "Play from here in loop"         , self.on_play_from_here_in_loop)
    self.add_to_menu(play_menu, 0, "Stop playing"                   , self.on_stop_playing)
    
    self.book_menu = self.add_to_menu(self.menubar, 1, "Songbook")
    self.add_to_menu(self.book_menu, 0, "New songbook"                      , self.on_new_songbook)
    self.add_separator_to_menu(self.book_menu)
    self.add_to_menu(self.book_menu, 0, "Songbook properties..."            , self.on_songbook_prop)
    self.add_separator_to_menu(self.book_menu)
    #self.no_songbook_menu = self.add_to_menu(book_menu, 0, "(no songbook opened)")
    #self.set_menu_enable(self.no_songbook_menu, False)
    self.songbook_songs_menu = []
    
    song_menu = self.add_to_menu(self.menubar, 1, "Song")
    self.add_to_menu(song_menu, 0, "New song"                          , self.on_new)
    self.add_separator_to_menu(song_menu)
    self.add_to_menu(song_menu, 0, "Song and instruments properties...", self.on_song_prop)
    
    instru_menu = self.add_to_menu(self.menubar, 1, "Instrument")
    self.add_to_menu(instru_menu, 0, "Add..."       , self.on_add_instrument)
    self.add_to_menu(instru_menu, 0, "Duplicate"    , self.on_dupplicate_instrument)
    self.add_to_menu(instru_menu, 0, "Remove"       , self.on_remove_instrument)
    self.add_to_menu(instru_menu, 0, "Move up"      , self.on_move_instrument_up)
    self.add_to_menu(instru_menu, 0, "Move down"    , self.on_move_instrument_down)
    self.add_separator_to_menu(instru_menu)
    self.add_to_menu(instru_menu, 0, "Instrument properties..."      , self.on_instrument_prop)
    
    note_menu = self.add_to_menu(self.menubar, 1, "Note")
    self.add_to_menu(note_menu, 0, "One octavo above", lambda *args: self.canvas and self.canvas.shift_selections_values( 12))
    self.add_to_menu(note_menu, 0, "One pitch above" , lambda *args: self.canvas and self.canvas.shift_selections_values( 1), accel = "+", accel_enabled = 0)
    self.add_to_menu(note_menu, 0, "One pitch below" , lambda *args: self.canvas and self.canvas.shift_selections_values(-1), accel = "-", accel_enabled = 0)
    self.add_to_menu(note_menu, 0, "One octavo below", lambda *args: self.canvas and self.canvas.shift_selections_values(-12))
    self.add_separator_to_menu(note_menu)
    self.add_to_menu(note_menu, 0, "Delete"                  , lambda *args: self.canvas and self.canvas.delete_notes(self.canvas.selections), accel = "Del", accel_enabled = 0)
    self.add_to_menu(note_menu, 0, "Arrange notes at fret...", self.on_note_arrange)
    self.add_to_menu(note_menu, 0, "Note properties..."                 , self.on_note_prop)
    
    for duration in [384, 192, 96, 48, 24, 12]:
      def f(event, duration = duration):
        if self.updating_menu or not self.canvas: return
        if self.canvas.selections:
          self.canvas.current_duration = duration
          notes = list(self.canvas.selections)
          old_durations = [note.duration for note in notes]
          
          def do_it(notes = notes):
            for note in notes:
              dotted  = note.is_dotted()
              triplet = note.is_triplet()
              note.duration = duration
              if dotted : note.duration *= 1.5
              if triplet: note.duration  = (note.duration * 2) // 3
              
          def undo_it(notes = notes):
            for i in range(len(notes)): notes[i] = old_durations[i]
            
          editobj3.undoredo.UndoableOperation(do_it, undo_it, _("change of %s") % _("duration"), self.undo_stack)
          
      setattr(self, "set_duration_%s" % duration, f)
    
    def toggle_dotted(*args):
      if self.canvas and not self.updating_menu: self.canvas.toggle_dotted()
    def toggle_triplet(*args):
      if self.canvas and not self.updating_menu: self.canvas.toggle_triplet()
    def toggle_accent(*args):
      if self.canvas and not self.updating_menu: self.canvas.toggle_accent()
    self.toggle_dotted  = toggle_dotted
    self.toggle_triplet = toggle_triplet
    self.toggle_accent  = toggle_accent 
    
    def on_duration_menu_cliked(*args):
      self.updating_menu = True
      if self.canvas and self.canvas.selections:
        note = tuple(self.canvas.selections)[0]
        self.set_menu_checked(dotted , note.is_dotted ())
        self.set_menu_checked(triplet, note.is_triplet())
      self.updating_menu = False
        
    duration_menu = self.add_to_menu(self.menubar, 1, "Duration", on_duration_menu_cliked)
    self.add_to_menu(duration_menu, 0, "Whole"        , self.set_duration_384, image = self.menu_image("note_384.png"))
    self.add_to_menu(duration_menu, 0, "Half"         , self.set_duration_192, image = self.menu_image("note_192.png"))
    self.add_to_menu(duration_menu, 0, "Quarter"      , self.set_duration_96 , image = self.menu_image("note_96.png"))
    self.add_to_menu(duration_menu, 0, "Eighth"       , self.set_duration_48 , image = self.menu_image("note_48.png"))
    self.add_to_menu(duration_menu, 0, "Sixteenth"    , self.set_duration_24 , image = self.menu_image("note_24.png"))
    self.add_to_menu(duration_menu, 0, "Thirty-second", self.set_duration_12 , image = self.menu_image("note_12.png"))
    self.add_separator_to_menu(duration_menu)
    dotted  = self.add_to_menu(duration_menu, 0, "Dotted"       , toggle_dotted , type = "check", accel = ".", accel_enabled = 0)
    triplet = self.add_to_menu(duration_menu, 0, "Triplet"      , toggle_triplet, type = "check")
    self.add_separator_to_menu(duration_menu)
    self.add_to_menu(duration_menu, 0, "Longer"       , self.set_duration_longer , accel = "*")
    self.add_to_menu(duration_menu, 0, "Shorter"      , self.set_duration_shorter, accel = "/")
    
    
    def on_volume_fx_menu_cliked(*args):
      self.updating_menu = True
      if self.canvas and self.canvas.selections:
        note = tuple(self.canvas.selections)[0]
        if   note.volume == 255:       self.set_menu_checked(volume_menus[0], True)
        else:                          self.set_menu_checked(volume_menus[0], False)
        if   190 < note.volume  < 255: self.set_menu_checked(volume_menus[1], True)
        else:                          self.set_menu_checked(volume_menus[1], False)
        if   100 < note.volume <= 190: self.set_menu_checked(volume_menus[2], True)
        else:                          self.set_menu_checked(volume_menus[2], False)
        if   note.volume <= 100:       self.set_menu_checked(volume_menus[3], True)
        else:                          self.set_menu_checked(volume_menus[3], False)
        
        fxs = set([note.link_fx, note.duration_fx, note.strum_dir_fx])
        if note.fx == "bend": fxs.add("bend%s" % note.bend_pitch)
        else:                  fxs.add(note.fx)
        for key, menu in fx_menus.items():
          self.set_menu_checked(menu, key in fxs)
      self.updating_menu = False

    for volume in [255, 204, 120, 50]:
      def f(event, volume = volume):
        if self.canvas and not self.updating_menu: self.canvas.set_selections_volume(volume)
      setattr(self, "set_volume_%s" %  volume, f)
      
    for type, fxs in model.ALL_FXS:
      if type: type += "_"
      for fx in fxs:
        if not fx: continue
        for arg in model.FXS_ARGS.get(fx, [None]):
          def f(event, type = type, fx = fx, arg = arg):
            if self.canvas and not self.updating_menu: getattr(self.canvas, "set_selections_%sfx" % type)(fx, arg)
          if arg: setattr(self, "set_fx_%s%s" % (fx, str(arg).replace(".", "")), f)
          else:   setattr(self, "set_fx_%s"   %  fx, f)
          
    effect_menu = self.add_to_menu(self.menubar, 1, "Effect", on_volume_fx_menu_cliked)
    volume_menus = [
      self.add_to_menu(effect_menu, 0, "Accentuated"            , self.set_volume_255, type = "radio", accel = "Enter", accel_enabled = 0),
      self.add_to_menu(effect_menu, 0, "Normal"                 , self.set_volume_204, type = "radio"),
      self.add_to_menu(effect_menu, 0, "Low"                    , self.set_volume_120, type = "radio"),
      self.add_to_menu(effect_menu, 0, "Very low"               , self.set_volume_50 , type = "radio"),
      ]
    self.add_separator_to_menu(effect_menu)
    self.add_to_menu(effect_menu, 0, "Remove all effects"       , self.set_fx_none   , accel = "n", accel_enabled = 0)
    
    
    self.add_separator_to_menu(effect_menu)
    fx_menus = self.fx_menus = {
      "bend0.5" : self.add_to_menu(effect_menu, 0, "bend 0.5" , self.set_fx_bend05  , type = "check", accel = "b", accel_enabled = 0),
      "bend1.0" : self.add_to_menu(effect_menu, 0, "bend 1"   , self.set_fx_bend10  , type = "check"),
      "bend1.5" : self.add_to_menu(effect_menu, 0, "bend 1.5" , self.set_fx_bend15  , type = "check"),
      "tremolo" : self.add_to_menu(effect_menu, 0, "tremolo"  , self.set_fx_tremolo , type = "check", accel = "t", accel_enabled = 0),
      "dead"    : self.add_to_menu(effect_menu, 0, "dead note", self.set_fx_dead    , type = "check", accel = "d", accel_enabled = 0),
      "roll"    : self.add_to_menu(effect_menu, 0, "roll"     , self.set_fx_roll    , type = "check", accel = "r", accel_enabled = 0),
      "harmonic": self.add_to_menu(effect_menu, 0, "harmonic" , self.set_fx_harmonic, type = "check", accel = "h", accel_enabled = 0),
      }
    self.add_separator_to_menu(effect_menu)
    fx_menus.update({
      "appoggiatura": self.add_to_menu(effect_menu, 0, "appoggiatura", self.set_fx_appoggiatura, type = "check", accel = "a", accel_enabled = 0),
      "fermata"     : self.add_to_menu(effect_menu, 0, "fermata"     , self.set_fx_fermata     , type = "check", accel = "p", accel_enabled = 0),
      "breath"      : self.add_to_menu(effect_menu, 0, "breath"      , self.set_fx_breath      , type = "check"),
      })
    self.add_separator_to_menu(effect_menu)
    fx_menus.update({
      "link"  : self.add_to_menu(effect_menu, 0, "link" , self.set_fx_link   , type = "check", accel = "l", accel_enabled = 0),
      "slide" : self.add_to_menu(effect_menu, 0, "slide", self.set_fx_slide  , type = "check", accel = "s", accel_enabled = 0),
    })
    self.add_separator_to_menu(effect_menu)
    fx_menus.update({
      "up"         : self.add_to_menu(effect_menu, 0, "up"        , self.set_fx_up        , type = "check", accel = "^", accel_enabled = 0),
      "down"       : self.add_to_menu(effect_menu, 0, "down"      , self.set_fx_down      , type = "check", accel = "_", accel_enabled = 0),
      "down_thumb" : self.add_to_menu(effect_menu, 0, "down_thumb", self.set_fx_down_thumb, type = "check", accel = ",", accel_enabled = 0),
    })
    
    help_menu = self.add_to_menu(self.menubar, 1, "Help")
    self.add_to_menu(help_menu, 0, "About..."         , self.on_about)
    self.add_to_menu(help_menu, 0, "Manual..."        , self.on_manual, accel = "F1")
    self.add_separator_to_menu(help_menu)
    self.add_to_menu(help_menu, 0, "Dump"             , self.on_dump)
    self.add_to_menu(help_menu, 0, "GC"               , self.on_gc)
    
    
    songwrite3.plugins.create_plugins_ui(self)
    
    self.song     = None
    self.songbook = None
    self.instrument_chooser_pane = None
    self.paned    = None
    self.scrolled = None
    self.canvas   = None
    self.selected_partition = None
    self.selected_mesure    = None
    self.selected_note      = None
    
    if   isinstance(song, model.Song)    : self.set_songbook(None); self.set_song(song)
    elif isinstance(song, model.Songbook): self.set_songbook(song)
    else:                                  self.set_song    (None)
    
    self.window.closeEvent = self.closeEvent
    self.destroy           = self.window.destroy
    
    toolbar = self.toolbar = qtwidgets.QToolBar()
    self.add_to_menu(toolbar, 0, "Save",           self.on_save)
    self.add_to_menu(toolbar, 0, "preview_print",  self.on_preview_print)
    self.add_to_menu(toolbar, 0, "Play from here", self.on_play_from_here)
    self.add_to_menu(toolbar, 0, "Stop playing",   self.on_stop_playing)
    
    self.toolbar.addSeparator()
    
    radio_group = qtwidgets.QActionGroup(self.window)
    for duration in [384, 192, 96, 48, 24, 12]:
      action = self.add_to_menu(toolbar, 0, model.DURATIONS[duration], getattr(self, "set_duration_%s" % duration), image = self.menu_image("note_%s.png" % duration))
      action.setCheckable(True)
      radio_group.addAction(action)
      setattr(self, "toolbar_duration_%s" % duration, action)
    self.toolbar_dotted  = self.add_to_menu(toolbar, 0, "Dotted" , self.toggle_dotted , image = self.menu_image("note_144.png"))
    self.toolbar_triplet = self.add_to_menu(toolbar, 0, "Triplet", self.toggle_triplet, image = self.menu_image("note_64.png" ))
    self.toolbar_dotted .setCheckable(True)
    self.toolbar_triplet.setCheckable(True)
    
    self.toolbar.addSeparator()
    
    self.toolbar_accent = self.add_to_menu(toolbar, 0, "Accentuated", self.toggle_accent, image = self.menu_image("effet_accent.png" ))
    self.toolbar_accent.setCheckable(True)
    
    self.toolbar_buttons = {}
    for type, fxs in model.ALL_FXS:
      for fx in fxs:
        if not fx: continue
        if fx == "bend": func = self.set_fx_bend05
        else:            func = getattr(self, "set_fx_%s" % fx)
        self.toolbar_buttons[fx] = action = self.add_to_menu(toolbar, 0, fx, func, image = self.menu_image("effet_%s.png" % fx))
        action.setCheckable(True)
        
    zoom_levels = [0.25, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]
    
    def zoom_in (menu_item):
      if self.canvas: self.canvas.change_zoom( 1)
    def zoom_out(menu_item):
      if self.canvas: self.canvas.change_zoom(-1)
    def set_zoom(zoom):
      if self.canvas:
        zoom = int(zoom.replace("%", "")) / 100.0
        self.canvas.set_zoom(zoom)
    self.on_set_zoom = set_zoom
    
    zoom_toolbar = qtwidgets.QToolBar()
    zoom_out_menu = self.add_to_menu(zoom_toolbar, 0, " ‒ ", zoom_out)
    
    self.zoom_menu  = qtwidgets.QComboBox()
    for zoom in zoom_levels:
      self.zoom_menu.addItem("%s%%" % int(zoom * 100.0), zoom)
    self.zoom_menu.setFrame(False)
    self.zoom_menu.setCurrentText("100%")
    self.zoom_menu.currentTextChanged.connect(set_zoom)
    zoom_toolbar.addWidget(self.zoom_menu)
    zoom_in_menu  = self.add_to_menu(zoom_toolbar, 0, " + ", zoom_in)
    
    self.toolbar_layout = qtwidgets.QHBoxLayout()
    self.toolbar_layout.addWidget(toolbar, 1)
    self.toolbar_layout.addWidget(zoom_toolbar)
    self.layout.insertLayout(1, self.toolbar_layout)
    
    if globdef.config.WINDOW_WIDTH == 0:
      self.window.showMaximized()
    else:
      self.window.resize(globdef.config.WINDOW_WIDTH, globdef.config.WINDOW_HEIGHT)
      self.window.showNormal()
      
    if globdef.config.WINDOW_X != -1:
      self.window.move(globdef.config.WINDOW_X, globdef.config.WINDOW_Y)
      
  def create_content(self):
    self.window.setWindowTitle("Songwrite3")
    self.instrument_chooser_pane = InstrumentChooserPane(self)
    self.window.layout().addWidget(self.instrument_chooser_pane)
    
  def menu_image(self, filename):
    icon = qtgui.QIcon(os.path.join(globdef.DATADIR, filename))
    return icon
  
  def set_fx_none(self, *args):    self.canvas.remove_selections_fx()
  
  def set_selected_partition(self, partition):
    self.selected_partition = partition
    if self.partition_editor and partition:
      if self.partition_editor.window.isVisible(): self.partition_editor.edit(partition)
      else:                                        self.partition_editor = None
    
  def set_selected_mesure(self, mesure):
    self.selected_mesure = mesure
    if self.mesure_editor and mesure:
      if self.mesure_editor.window.isVisible(): self.mesure_editor.edit(mesure)
      else:                                     self.mesure_editor = None
      
  def set_selected_note(self, note):
    self.updating_menu = True
    self.selected_note = note
    if self.note_editor and note:
      if self.note_editor.window.isVisible(): self.note_editor.edit(note)
      else:                                   self.note_editor = None
    if isinstance(note, introsp.ObjectPack):
      mesure_ids = set([self.song.mesure_at(n).get_number() + 1 for n in note.objects])
      if len(mesure_ids) == 1:
        mesure_label = self.song.mesure_at(note.objects[0])
      else:
        mesure_label = _("Bars #%s to #%s") % (min(mesure_ids), max(mesure_ids))
      if len(note.objects) == 2:
        delta = abs(note.objects[0].value - note.objects[1].value)
        note_label = _("__interval__%s" % delta)
        if note_label.startswith("_"): note_label = "2 %s" % _("notes")
      else:
        note_label = "%s %s" % (len(note.objects), _("notes"))
      note = note.objects[-1]
    else:
      mesure_label = self.song.mesure_at(note)
      note_label = str(note)
      
    current_duration = note.base_duration()
    self.set_menu_checked(getattr(self, "toolbar_duration_%s" % current_duration), True)
    self.set_menu_checked(self.toolbar_dotted , note.is_dotted())
    self.set_menu_checked(self.toolbar_triplet, note.is_triplet())
    self.set_menu_checked(self.toolbar_accent , note.volume == 255)
    
    fxs = { note.fx, note.link_fx, note.duration_fx, note.strum_dir_fx }
    for key, button in self.toolbar_buttons.items(): self.set_menu_checked(button, key in fxs)
    
    self.window.setWindowTitle("Songwrite3 -- %s -- %s -- %s" % (self.song.title, mesure_label, note_label))
    self.updating_menu = False
      
  def get_selected_notes(self):
    if isinstance(self.selected_note, introsp.ObjectPack): return self.selected_note.objects
    return [self.selected_note]
  
  def partition_categories(self):
    next_strophe_number = len([lyrics for lyrics in self.song.partitions if isinstance(lyrics, model.Lyrics) and _("Strophe #%s").replace("%s", "") in lyrics.header]) + 1
    
    return PartitionCategory(_("Available score views"), _("Select the score and score view you want to add."),
        [model.Partition(None, view_type.default_instrument, view_type) for view_type in [model.GuitarView, model.BassView]] +
        [PartitionCategory(_("More tablatures..."), _("Tablature (for guitar-like instruments)"),
          [model.Partition(None, view_type.default_instrument, view_type) for view_type in model.VIEWS["tab"] if not view_type is model.GuitarView and not view_type is model.BassView])
        ] +
        [model.Partition(None, view_type.default_instrument, view_type) for view_type in [model.PianoView, model.GuitarStaffView, model.VocalsView]] +
        [PartitionCategory(_("More staffs..."), _("Staff (for any instrument)"),
          [model.Partition(None, view_type.default_instrument, view_type) for view_type in model.VIEWS["staff"] if not view_type is model.PianoView and not view_type is model.VocalsView and not view_type is model.GuitarStaffView])
        ] +
        [model.Partition(None, model.TomView.default_instrument, model.TomView)] +
        [PartitionCategory(_("More drums..."), _("Drum tablatures (for drums)"),
          [model.Partition(None, view_type.default_instrument, view_type) for view_type in model.VIEWS["drums"] if not view_type is model.TomView])
        ] +
        [
        model.Lyrics(None, header = _("Chorus")),
        model.Lyrics(None, header = _("Strophe #%s") % next_strophe_number),
        ])

  def edit(self, o, *args, **kargs):
    return editobj3.edit(o, undo_stack = self.undo_stack, master = self, menubar = False, *args, **kargs)
  
  def on_new_app(self, *args): self.__class__()
  
  def close_dialog(self, *args): self.closeEvent(None)
    
  def closeEvent(self, e):
    if self.check_save():
      if e: e.ignore()
      return
    if e: e.accept()
    
    if self.song: del APPS[self.song]
    if self.songbook: del APPS[self.songbook]
    self.destroy()
    
    if len(APPS) == 0:
      globdef.config.WINDOW_X = self.window.x()
      globdef.config.WINDOW_Y = self.window.y()
      if self.window.isMaximized():
        globdef.config.WINDOW_WIDTH  = globdef.config.WINDOW_HEIGHT = 0
      else:
        globdef.config.WINDOW_WIDTH  = self.window.width()
        globdef.config.WINDOW_HEIGHT = self.window.height()
      globdef.config.save()
      sys.exit()

      
  def prompt_open_filename(self, exts = [".sw.xml"], typename = "", title = None):
    ext_label = self.get_ext_label(exts, typename)
    if self.filename: dirname = self.filename
    else:             dirname = ""
    filename = qtwidgets.QFileDialog.getOpenFileName(self.window, title or _("Open..."), dirname, ext_label)[0]
    return filename
  
  def prompt_save_filename(self, exts = [".sw.xml"], typename = "", title = None):
    ext_label = self.get_ext_label(exts, typename)
    if self.filename:
      filename  = self.filename.split(".")[0] + exts[0]
    else:
      filename  = remove_accents(self.song.title.lower().replace(" ", "_").replace("'", "").replace("/", "_")) + exts[0]
      
    filename = qtwidgets.QFileDialog.getSaveFileName(self.window, title or _("Save as..."), filename, ext_label)[0]
    if filename:
      for ext in exts:
        if filename.endswith(ext): break
      else:
        filename += exts[0]
    return filename
  
  def get_ext_label(self, exts, typename):
    if exts == [".sw.xml"]:
      ext_label = _("__songwrite_file_format__") + " (*.sw.xml)"
    else:
      exts_joined = " ".join("*%s" % ext for ext in exts)
      typename    = typename or exts_joined
      ext_label   = "%s %s (%s)" % (_("Files"), typename, exts_joined)
    return ext_label + ";;%s (*.*)" % _("__all_files__")

  
  def on_open(self, event = None):
    if self.check_save(): return
    
    filename = self.prompt_open_filename()
    if filename:
      self.open_filename(filename, do_check_save = 0) # check_save has already been done before asking the filename
      
  def check_save(self):
    if not self.song: return False
    
    if self.undo_stack.undoables == self.last_undoables: return 0 # The undoable actions have not changed => nothing to save.
    msg = qtwidgets.QMessageBox()
    msg.setText(_("Save modifications before closing?"))
    #msg.setStandardButtons(qtwidgets.QMessageBox.Save | qtwidgets.QMessageBox.Discard | qtwidgets.QMessageBox.Cancel)
    #msg.setDefaultButton(qtwidgets.QMessageBox.Cancel)
    save_button    = msg.addButton(_("Save"), 0)
    discard_button = msg.addButton(_("Close without saving"), 0)
    cancel_button  = msg.addButton(_("Cancel"), 0)
    msg.setDefaultButton(cancel_button)
    msg.setEscapeButton(cancel_button)
    ret = msg.exec()
    if   ret == 1: return False
    elif ret == 2: return True
    elif ret == 0:
      self.on_save()
      return self.check_save() # The user may have canceled the "save as" dialog box !
    
  def set_song(self, song):
    if self.song:
      del APPS[self.song]
      if self.filename: model.unload_song(self.filename)
      
    self.undo_stack.clear()
    self.last_undoables = []
    self.song = song
    
    if self.instrument_chooser_pane:
      self.instrument_chooser_pane.hide()
      self.window.layout().addWidget(self.instrument_chooser_pane)
      self.instrument_chooser_pane.destroy()
      
    if self.canvas:
      zoom = self.canvas.zoom
      self.canvas.hide()
      self.window.layout().addWidget(self.canvas)
      self.canvas.destroy()
    else:
      zoom = 1.0
      
    if song:
      APPS[song] = self
      self.filename = song.filename
      self.window.setWindowTitle("Songwrite3 -- %s" % song.title)
      self.canvas = Canvas(self, self.song, zoom)
      self.window.layout().addWidget(self.canvas)
      
    else:
      self.window.setWindowTitle("Songwrite3")
      self.instrument_chooser_pane = InstrumentChooserPane(self)
      self.window.layout().addWidget(self.instrument_chooser_pane)
      
    
  def set_songbook(self, songbook):
    if self.songbook:
      del APPS[self.songbook]
      unobserve(self.songbook.song_refs, self.on_songbook_changed)
      
    self.songbook = songbook
    
    if self.songbook:
      APPS[self.songbook] = self
      if self.songbook.song_refs: self.set_song(self.songbook.song_refs[0].get_song())
      observe(self.songbook.song_refs, self.on_songbook_changed)
      
    self.rebuild_songbook_menu()
    
  def rebuild_songbook_menu(self):
    for menu in self.songbook_songs_menu: self.book_menu.removeAction(menu)
    
    if self.songbook:
      self.songbook_songs_menu = []
      for song_ref in self.songbook.song_refs:
        def open_song(event, song_ref = song_ref):
          self.set_song(song_ref.get_song())
        menu = self.add_to_menu(self.book_menu, 0, song_ref.title, open_song)
        self.songbook_songs_menu.append(menu)
        
    else:
      no_songbook_menu = self.add_to_menu(self.book_menu, 0, "(no songbook opened)")
      self.set_menu_enable(no_songbook_menu, False)
      self.songbook_songs_menu = [no_songbook_menu]
      
  def on_songbook_changed(self, obj, type, new, old):
    self.rebuild_songbook_menu()
    
    
  def on_file_menu(self, *args):
    if self.songbook:
      self.set_menu_enable(self.save_as_songbook_menu      , 1)
      self.set_menu_enable(self.preview_print_songbook_menu, 1)
      self.set_menu_enable(self.export_songbook_menu       , 1)
    else:
      self.set_menu_enable(self.save_as_songbook_menu      , 0)
      self.set_menu_enable(self.preview_print_songbook_menu, 0)
      self.set_menu_enable(self.export_songbook_menu       , 0)
    
  def on_new(self, *args):
    if self.check_save(): return
    
    self.filename = None
    self.set_songbook(None)
    self.set_song    (None)
    
  def on_new_songbook(self, *args):
    if self.check_save(): return

    songbook = model.Songbook()
    songbook.authors   = getpass.getuser().title()
    songbook.title     = _("%s's songbook") % songbook.authors
    
    self.set_songbook(songbook)
    self.on_songbook_prop()
    
  def on_open(self, event = None):
    if self.check_save(): return
    
    filename = self.prompt_open_filename()
    if not filename: return
    self.open_filename(filename, do_check_save = 0) # check_save has already been done before asking the filename
    
  def open_filename(self, filename, do_check_save = 1):
    globdef.config.LAST_DIR = os.path.dirname(filename)
    
    if do_check_save and self.check_save(): return
    
    if not os.path.exists(filename):
      editobj3.edit(_("File does not exist!"), on_validate = lambda o: None)
    else:
      self.filename = filename
      song = model.get_song(filename)
      if isinstance(song, model.Song):
        self.set_songbook(None)
        self.set_song    (song)
      else:
        self.set_songbook(song)
        self.on_songbook_prop()
      globdef.config.add_previous_file(filename)
      
  def on_save_as(self, event = None):
    filename = self.prompt_save_filename()
    if not filename: return
    self.filename = self.song.filename = filename
    self.on_save(save_song = 1, save_songbook = 0)
    
  def on_save_as_songbook(self, event = None):
    filename = self.prompt_save_filename()
    if not filename: return
    if not filename.endswith(".sw.xml"): filename += ".sw.xml"
    self.songbook.set_filename(filename)
    self.on_save(save_song = 0, save_songbook = 1)
    
  def on_save(self, event = None, save_song = 1, save_songbook = 1):
    if not self.song: return
    if save_song:
      ok_song = 0
      
      if not self.filename: self.on_save_as()
      if self.filename:
        #self.song.__xml__(codecs.lookup("utf8")[3](open(self.filename, "w")))
        s = StringIO()
        self.song.__xml__(s)
        s = s.getvalue()
        open(self.filename, "w").write(s)
        ok_song = 1
        
        if not self.songbook: globdef.config.add_previous_file(self.filename)
        
    else: ok_song = 1
    
    
    if save_songbook and self.songbook:
      ok_songbook = 0
      
      if not self.songbook.filename: self.on_save_as_songbook()
      if self.songbook.filename:
        #self.songbook.__xml__(codecs.lookup("utf8")[3](open(self.songbook.filename, "w")))
        s = StringIO()
        self.songbook.__xml__(s)
        s = s.getvalue()
        open(self.songbook.filename, "w").write(s)
        ok_songbook = 1
        
        globdef.config.add_previous_file(self.songbook.filename)
        
    else: ok_songbook = 1
    
    
    if ok_song and ok_songbook: self.last_undoables = self.undo_stack.undoables[:]
    
  def on_preview_print(self, event = None):
    if not self.song: return
    try:
      songwrite3.plugins.get_exporter("pdf").print_preview(self.song)
    except:
      self._treat_export_error()
      
  def on_preview_print_songbook(self, event = None):
    if not self.songbook: return
    try:
      songwrite3.plugins.get_exporter("pdf").print_preview(self.songbook)
    except:
      self._treat_export_error()
      
  def _treat_export_error(self):
    error_class, error, trace = sys.exc_info()
    sys.excepthook(error_class, error, trace)
    print(file = sys.stderr)
    
    if isinstance(error, model.SongwriteError):
      editobj3.edit(error)
      if isinstance(error, model.TimeError):
        self.canvas.deselect_all()
        if   error.note:
          self.canvas.partition_2_drawer[error.note.partition].select_note(error.note)
        elif error.partition and error.time:
          self.canvas.partition_2_drawer[error.partition].select_at(error.time, 0, 0)
        elif error.time:
          self.canvas.partition_2_drawer[self.song.partitions[0]].select_at(error.time, 0, 0)
    else:
      editobj3.edit(_(error.__class__.__name__) + "\n\n" + str(error))
      
      
  def on_about(self, *args):
    class About(object):
      def __init__(self):
        self.details       = _("__about__")
        self.icon_filename = os.path.join(globdef.DATADIR, "songwrite_about.png")
        self.url           = "http://www.lesfleursdunormal.fr/static/informatique/songwrite/index_en.html"
        self.licence       = "GPL"
        self.authors       = "Jean-Baptiste 'Jiba' Lamy <jibalamy@free.fr>"
        
      def __str__(self): return "Songwrite 3 version %s" % model.VERSION
      
    descr = introsp.description(About)
    descr.def_attr("details"      , field.HiddenField)
    descr.def_attr("icon_filename", field.HiddenField)
    self.edit(About())
    
  def on_manual(self, *args):
    DOCDIR = os.path.join(globdef.APPDIR, "doc")
    if not os.path.exists(DOCDIR):
      import glob
      DOCDIR = glob.glob(os.path.join(globdef.APPDIR, "..", "doc", "songwrite3*"))[0]
      
      if not os.path.exists(DOCDIR):
        DOCDIR = glob.glob("/usr/share/doc/songwrite3*")[0]
      
        if not os.path.exists(DOCDIR):
          DOCDIR = glob.glob("/usr/share/local/doc/songwrite3*")[0]
          
          if not os.path.exists(DOCDIR):
            DOCDIR = glob.glob("/usr/doc/songwrite3")[0]
            
    DOC = os.path.join(DOCDIR, locale.getdefaultlocale()[0][:2], "doc.pdf")
    if not os.path.exists(DOC):
      DOC = os.path.join(DOCDIR, "en", "doc.pdf")
      
    DOC = os.path.abspath(DOC)
    pdf_command = globdef.config.get_preview_command_pdf()
    if "%s" in pdf_command:
      #os.system(pdf_command % DOC)
      p = subprocess.Popen(pdf_command % DOC, shell = True, close_fds = True)
    else:
      if pdf_command.endswith("-"): pdf_command = pdf_command[-1]
      #os.system(pdf_command + " " + DOC)
      p = subprocess.Popen(pdf_command + " " + DOC, shell = True, close_fds = True)
      
  def on_add_instrument(self, event = None):
    if self.selected_partition:
      if isinstance(self.selected_partition, introsp.ObjectPack): selected_partition = self.selected_partition.objects[-1]
      else:                                                       selected_partition = self.selected_partition
    else:                                                         selected_partition = None
    def callback(*args): pass
    
    song = self.song or new_song()
    descr = introsp.description(model.Song)
    if selected_partition:
      action = introsp.InsertAction(descr.attributes["partitions"])
      new_child = descr.do_action(action, self.undo_stack, None, song, descr.attributes["partitions"], selected_partition, callback)
    else:
      action = introsp.AppendAction(descr.attributes["partitions"])
      new_child = descr.do_action(action, self.undo_stack, None, song, callback)
    if not self.song is song: self.set_song(song)
    
  def on_dupplicate_instrument(self, event = None):
    if not self.song: return
    if isinstance(self.selected_partition, introsp.ObjectPack):
      partitions = self.selected_partition.objects
    else: partitions = [self.selected_partition]
    
    insert_at = max([self.song.partitions.index(partition) for partition in partitions])
    
    xml = StringIO()
    xml.write("<song>\n")
    context = model._XMLContext()
    for partition in partitions: partition.__xml__(xml, context)
    xml.write("</song>")
    
    import songwrite3.stemml as stemml
    xml.seek(0)
    song = stemml.parse(xml)
    
    def do_it(song = song):
      for partition in song.partitions:
        self.song.insert_partition(insert_at, partition)
        partition.song = self.song
    def undo_it(song = song):
      for partition in song.partitions:
        self.song.remove_partition(partition)
    undoredo.UndoableOperation(do_it, undo_it, _("Duplicate instrument"), self.undo_stack)
    
  def on_remove_instrument(self, event = None):
    if self.song and self.selected_partition:
      descr = introsp.description(self.song.__class__)
      descr.do_action(introsp._REMOVE_ACTION, self.undo_stack, None, self.song, descr.attributes["partitions"], self.selected_partition)
      self.set_selected_partition(None)
      
  def on_move_instrument_up(self, event = None):
    if self.song and self.selected_partition:
      descr = introsp.description(self.song.__class__)
      descr.do_action(introsp._MOVE_UP_ACTION, self.undo_stack, None, self.song, descr.attributes["partitions"], self.selected_partition)
      
  def on_move_instrument_down(self, event = None):
    if self.song and self.selected_partition:
      descr = introsp.description(self.song.__class__)
      descr.do_action(introsp._MOVE_DOWN_ACTION, self.undo_stack, None, self.song, descr.attributes["partitions"], self.selected_partition)
    
  def on_song_prop(self, event = None):
    if self.song: self.edit(self.song)
    
  def on_instrument_prop(self, event = None):
    if self.song and self.selected_partition:
      self.partition_editor = self.edit(self.selected_partition)
      self.partition_editor.window.resize(self.partition_editor.window.width(), app.desktop().screenGeometry(self.window).height() * 0.8)
     
  def on_note_prop(self, event = None):
    if self.selected_note: self.note_editor = self.edit(self.selected_note)
    
  def on_songbook_prop(self, event = None):
    if not self.songbook:
      self.on_new_songbook()
      return
    
    def on_edit_child(song_ref):
      if isinstance(song_ref, model.SongRef):
        self.set_song(song_ref.get_song())
        
    self.edit(self.songbook, on_edit_child = on_edit_child)
    
  def on_bars_prop(self, event = None):
    mesures = self.canvas.get_selected_mesures()
    if mesures:
      if len(mesures) == 1: mesures = mesures[0]
      else:                 mesures = introsp.ObjectPack(mesures)
      self.mesure_editor = self.edit(mesures)
      
  def on_playlist_prop(self, event = None):
    if self.song:
      editor = self.edit(self.song.playlist)
      editor.window.resize(650, 400)
    
  def on_preferences(self, *args):
    globdef.config.edit()
    
  def on_play(self, *args):
    if self.canvas:
      player.play(songwrite3.midi.song_2_midi(self.song, trackable = 1), 0, self.canvas.play_tracker)
  def on_play_in_loop(self, *args):
    if self.canvas:
      player.play(songwrite3.midi.song_2_midi(self.song, trackable = 1), 1, self.canvas.play_tracker)
  def on_play_from_here(self, *args):
    if self.canvas:
      if player.is_playing(): player.stop()
      else:                   player.play(songwrite3.midi.song_2_midi(self.song, self.canvas.get_selected_time(), trackable = 1), 0, self.canvas.play_tracker)
  def on_play_from_here_in_loop(self, *args):
    if self.canvas:
      player.play(songwrite3.midi.song_2_midi(self.song, self.canvas.get_selected_time(), trackable = 1), 1, self.canvas.play_tracker)
  def on_stop_playing(self, *args):
    player.stop()
  
  def on_space(self, *args): # space : play from the current position
    if player.is_playing(): player.stop()
    else: self.on_play_from_here()
    
          
  def on_select_all(self, *args):
    if self.canvas: self.canvas.select_all()
    
  def on_note_cut(self, *args):
    if self.canvas: self.canvas.on_cut()
    
  def on_note_copy(self, *args):
    if self.canvas: self.canvas.on_copy()
    
  def on_note_paste(self, *args):
    if self.canvas: self.canvas.on_paste()
    
  def on_insert_times(self, *args):
    if not self.canvas: return
    class InsertTimesOptions(object):
      def __init__(self):
        self.nb_time       = 1
        self.details       = _("""Use negative values for deleting beats.""")
        self.icon_filename = os.path.join(globdef.DATADIR, "song.png")
      def __str__(self): return _("Insert/remove beats...")
    
    o = InsertTimesOptions()
    
    def on_validate(o):
      if (not o) or (not o.nb_time): return
      at = self.canvas.get_selected_time()
      delta = o.nb_time * 96
      removed = []
      
      def shift(delta):
        old_removed = removed[:]
        del removed[:]

        for partition in self.song.partitions:
          if isinstance(partition, model.Partition):
            i = 0
            while i < len(partition.notes):
              note = partition.notes[i]
              if note.time >= at:
                if (delta < 0) and note.time < at - delta:
                  partition.remove(partition.notes[i])
                  removed.append((partition, note))
                  continue
                else: note.time += delta
              i += 1
              
        for partition, note in old_removed: partition.add_note(note)
        
        self.song.rythm_changed()
        
        self.canvas.render_all()
        self.canvas.update_time()
        
      def do_it  (): shift( delta)
      def undo_it(): shift(-delta)

      if o.nb_time > 0: name = _("Insert %s beat(s)") %  o.nb_time
      else:             name = _("Delete %s beat(s)") % -o.nb_time
      undoredo.UndoableOperation(do_it, undo_it, name, self.undo_stack)
      
    editobj3.edit(o, on_validate = on_validate, menubar = False)
    
  def on_insert_bars(self, *args):
    if not self.canvas: return
    class InsertBarsOptions(object):
      def __init__(self):
        self.nb_bar        = 1
        self.details       = _("""Use negative values for deleting bars.""")
        self.icon_filename = os.path.join(globdef.DATADIR, "song.png")
      def __str__(self): return _("Insert/remove bars...")
    
    o = InsertBarsOptions()

    def on_validate(o):
      if (not o) or (not o.nb_bar): return
    
      mesures = self.canvas.get_selected_mesures()
      if mesures: mesure = mesures[0]
      else:       mesure = self.song.mesures[0]
      
      mesure_pos = self.song.mesures.index(mesure)
      at = mesure.time
      removed = []
      playlist_items_values = []
      
      def shift(nb_bar):
        # Add / remove mesures
        time = self.song.mesures[mesure_pos].time
        if nb_bar > 0:
          for i in range(mesure_pos, mesure_pos + nb_bar):
            self.song.mesures.insert(i, model.Mesure(self.song, time, mesure.tempo, mesure.rythm1, mesure.rythm2, mesure.syncope))
            time += mesure.duration
        else:
          del self.song.mesures[mesure_pos : mesure_pos - nb_bar]
          i = mesure_pos
          
        # Shift playlist
        if playlist_items_values:
          for item, from_mesure, to_mesure in playlist_items_values:
            item.from_mesure = from_mesure
            item.to_mesure   = to_mesure
          del playlist_items_values[:]
        else:
          for item in self.song.playlist.playlist_items:
            playlist_items_values.append((item, item.from_mesure, item.to_mesure))
            if   item.from_mesure >= mesure_pos:
              if item.from_mesure <  mesure_pos - nb_bar: item.from_mesure  = mesure_pos
              else:                                       item.from_mesure += nb_bar
            if   item.to_mesure   >= mesure_pos - 1:
              if item.to_mesure   <  mesure_pos-1-nb_bar: item.to_mesure   = mesure_pos - 1
              else:                                       item.to_mesure  += nb_bar
              
        # Shift notes
        old_removed = removed[:]
        del removed[:]

        delta = nb_bar * mesure.duration
        for partition in self.song.partitions:
          if isinstance(partition, model.Partition):
            i = 0
            while i < len(partition.notes):
              note = partition.notes[i]
              if note.time >= at:
                if (delta < 0) and note.time < at - delta:
                  partition.remove(partition.notes[i])
                  removed.append((partition, note))
                  continue
                else: note.time += delta
              i += 1
              
        for partition, note in old_removed: partition.add_note(note)

        self.song.rythm_changed() # AFTER moving the notes !!!
        
        self.canvas.render_all()
        self.canvas.update_time()
        
      def do_it  (): shift( o.nb_bar)
      def undo_it(): shift(-o.nb_bar)
      
      if o.nb_bar > 0: name = _("Insert %s bar(s)") %  o.nb_bar
      else:            name = _("Delete %s bar(s)") % -o.nb_bar
      undoredo.UndoableOperation(do_it, undo_it, name, self.undo_stack)
      
    editobj3.edit(o, on_validate = on_validate, menubar = False)
    
  def on_note_arrange(self, *args):
    if not self.canvas: return
    class ArrangeAtFretOptions(object):
      def __init__(self):
        self.fret          = 0
        self.details       = _("Arrange selected notes at fret?")
        self.icon_filename = os.path.join(globdef.DATADIR, "song.png")
      def __str__(self): return _("Arrange notes at fret...")
    
    o = ArrangeAtFretOptions()
    
    def on_validate(o):
      if o: self.canvas.arrange_selection_at_fret(o.fret)
        
    editobj3.edit(o, on_validate = on_validate, menubar = False)
        
  def on_dump(self, *args):
    if not self.song: return
    print(self.song.__xml__().getvalue(), file = sys.stderr)
    
  def on_gc(self, *args):
    import gc
    print(gc.collect(), "object(s) collected", file = sys.stderr)
    for o in gc.garbage: print("Garbage:", o, file = sys.stderr)
    print(file = sys.stderr)
    
    #import memtrack, weakref
    #ref = weakref.ref(self.songbook.song_refs[0].get_song())
    #if ref(): memtrack.reverse_track(ref())
    
    scan()
    
  def set_duration_longer (self): self.set_duration_longer_or_shorter(True)
  def set_duration_shorter(self): self.set_duration_longer_or_shorter(False)
  def set_duration_longer_or_shorter(self, longer):
    if not self.canvas: return
    if longer: notes = [note for note in self.canvas.selections if note.base_duration() < 384]
    else:      notes = [note for note in self.canvas.selections if note.base_duration() > 12 ]
    def decrease_duration(notes = notes):
      for note in notes: self.canvas.current_duration = note.duration = note.duration // 2
    def increase_duration(notes = notes):
      for note in notes: self.canvas.current_duration = note.duration = note.duration *  2
      
    if longer: undoredo.UndoableOperation(increase_duration, decrease_duration, _("increase note duration"), self.undo_stack)
    else:      undoredo.UndoableOperation(decrease_duration, increase_duration, _("decrease note duration"), self.undo_stack)
    
  def set_note_menus_enabled(self, enabled):
    # Needed because Qt considers AltGr + 8 (= backslash \) as a "_" for menu accels
    for menu in self.fx_menus.values(): self.set_menu_enable(menu, enabled)
    
  def on_pipe_command_received(self, info_message):
    print("EMITTED", info_message)
    




class InstrumentChooserPane(qtwidgets.QWidget):
  def __init__(self, main):
    qtwidgets.QWidget.__init__(self)
    layout    = qtwidgets.QVBoxLayout()
    
    layout.addWidget(qtwidgets.QLabel(), 3)
    
    label     = qtwidgets.QLabel("%s\n " % _("Choose an instrument:"))
    layout.addWidget(label, 0, qtcore.Qt.AlignHCenter)
    
    image     = qtwidgets.QLabel()
    pixmap    = qtgui.QPixmap(os.path.join(globdef.DATADIR, "instruments.png"), "png")
    image.setPixmap(pixmap)
    image.mouseReleaseEvent = self.on_mouse_release
    layout.addWidget(image, 0, qtcore.Qt.AlignHCenter)
    
    layout.addWidget(qtwidgets.QLabel(), 2)
    
    self.setLayout(layout)
    self.main         = main
    self.image        = image
    self.pixmap_width = pixmap.width()
    
  def on_mouse_release(self, event):
    x = event.x()
    if not(0 <= x < self.pixmap_width): return
    
    s = new_song()
    p = model.Partition(s)
    s.partitions.append(p)
    if   x < 100:
      p.view = model.GuitarView(p)
      sound_file = "son_guitare.mid"
    elif x < 168:
      from songwrite3.plugins.lyre import SevenStringLyreView
      p.view = SevenStringLyreView(p)
      sound_file = "son_lyre.mid"
    elif x < 255:
      p.view = model.VocalsView(p)
      sound_file = "son_chant.mid"
    elif x < 362:
      from songwrite3.plugins.accordion import AccordionView
      from songwrite3.plugins.chord     import AccordionChordView
      p.view = AccordionView(p)
      p2 = model.Partition(s)
      s.partitions.append(p2)
      p2.view = AccordionChordView(p2)
      p2.volume = 128
      sound_file = "son_accordeon.mid"
    else:
      from songwrite3.plugins.fingering import TinWhistleView
      p.view = TinWhistleView(p)
      sound_file = "son_flute.mid"
      
    player.play(open(os.path.join(globdef.DATADIR, sound_file), "rb").read())
    
    for p in s.partitions: p.instrument = p.view.default_instrument
    self.main.filename = None
    self.main.set_song(s)
    
    
def new_song():
  s = model.Song()
  s.authors   = getpass.getuser().title()
  s.title     = _("%s's song") % s.authors
  s.copyright = "Copyright %s by %s" % (time.localtime(time.time())[0], s.authors)
  return s
