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

# GlobDef : global stuff (cannot be called global nor glob so...).

import sys, os, os.path, gettext

APPDIR = os.path.dirname(__file__)

DATADIR = os.path.join(APPDIR, "data")
if not os.path.exists(DATADIR):
  import warnings
  warnings.warn("Songwrite3's data directory cannot be found !")
  
LOCALEDIR = os.path.join(APPDIR, "locale")
if not os.path.exists(LOCALEDIR):
  LOCALEDIR = os.path.join(APPDIR, "..", "locale")
  if not os.path.exists(LOCALEDIR):
    LOCALEDIR = os.path.join("/", "usr", "share", "locale")
    
try:
  translator = gettext.translation("songwrite3", LOCALEDIR)
except IOError: # Non-supported language, defaults to english
  translator = gettext.translation("songwrite3", LOCALEDIR, ("en",))
translator.install()

CONFIGFILE = os.path.expanduser(os.path.join("~", ".songwrite3"))
NO_CONFIG  = 0

class Config:
  def __init__(self):
    # Default config
    self.MIDI_COMMAND             = "timidity -idt -Wd -"
    self.MIDI_USE_TEMP_FILE       = 0
    self.PREVIEW_COMMAND_PDF      = ""
    self.PREVIEW_COMMAND_PDF2     = ""
    self.NUMBER_OF_UNDO           = 20
    self.PREVIOUS_FILES           = []
    self.PAGE_FORMAT              = "a4paper"
    self.PAGE_MARGIN_TOP          = 1.0
    self.PAGE_MARGIN_BOTTOM       = 2.0
    self.PAGE_MARGIN_INTERIOR     = 1.0
    self.PAGE_MARGIN_EXTERIOR     = 1.0
    self.DISPLAY_PLAY_BAR         = 1
    self.ASK_FILENAME_ON_EXPORT   = 1
    self.LAST_DIR                 = ""
    self.PLAY_AS_TYPING           = 1
    self.NUMBER_OF_PREVIOUS_FILES = 12
    self.AUTOMATIC_DURATION       = 1
    self.FONTSIZE                 = 0
    self.ENGLISH_CHORD_NAME       = 0
    self.WINDOW_X                 = -1 # -1 = auto
    self.WINDOW_Y                 = -1
    self.WINDOW_WIDTH             = 0 # 0 = maximized
    self.WINDOW_HEIGHT            = 0
    
    global NO_CONFIG
    if os.path.exists(CONFIGFILE):
      try:
        exec(compile(open(CONFIGFILE).read(), CONFIGFILE, 'exec'), self.__dict__)
        
        NO_CONFIG = 0
        return
      except:
        sys.excepthook(*sys.exc_info())
        print("Error in config file ~/.songwrite3 ! Please reconfigure Songwrite3 !", file = sys.stderr)
        
    NO_CONFIG = 1

  def get_preview_command_pdf(self):
    if not self.PREVIEW_COMMAND_PDF2:
      if self.PREVIEW_COMMAND_PDF:
        self.PREVIEW_COMMAND_PDF2 = self.PREVIEW_COMMAND_PDF
      else:
        from distutils.spawn import find_executable
        msg = _("Searching for PDF command: ")
        msgs = []
        for command in ["atril", "evince", "okular", "mupdf", "xpdf"]:
          path = find_executable(command)
          if path:
            self.PREVIEW_COMMAND_PDF2 = "%s %%s" % path
            msgs.append(command + _(": found"))
            break
          else:
            msgs.append(command + _(": not found"))
        print(msg + ", ".join(msgs), file = sys.stderr)
    return self.PREVIEW_COMMAND_PDF2
  
  def add_previous_file(self, file):
    try: self.PREVIOUS_FILES.remove(file) # No dupplicated item.
    except: pass
    self.PREVIOUS_FILES.insert(0, file)
    while len(self.PREVIOUS_FILES) > self.NUMBER_OF_PREVIOUS_FILES: del self.PREVIOUS_FILES[-1]
    
  def __str__(self):
    return """
# Songwrite config file. Use a Python syntax.

# 1 to use a temporary MIDI file (call this file %%s in the command line).
# 0 to use standard input.
MIDI_USE_TEMP_FILE = %s

# Command line to play a midi file.
MIDI_COMMAND = "%s"

# Page format (LaTeX)
PAGE_FORMAT = "%s"
PAGE_MARGIN_TOP      = %s
PAGE_MARGIN_BOTTOM   = %s
PAGE_MARGIN_INTERIOR = %s
PAGE_MARGIN_EXTERIOR = %s

# Command line to preview/print PDF (empty string for auto-detection).
PREVIEW_COMMAND_PDF = "%s"

# Size of undo stack.
NUMBER_OF_UNDO = %s

# Previous opened files.
PREVIOUS_FILES = %s

# Should the note currently being played be highlighted?
DISPLAY_PLAY_BAR = %s

# Should a "save as" dialog box be displayed before exporting?
ASK_FILENAME_ON_EXPORT = %s

# Last used directory
LAST_DIR = "%s"

# Play the note when they are entered
PLAY_AS_TYPING = %s

# Number of previous files in the file menu
NUMBER_OF_PREVIOUS_FILES = %s

# Automatically change previous note's duration when entering a new note
AUTOMATIC_DURATION = %s

# Interface font size (0 : auto)
FONTSIZE = %s

# Force English chord name
ENGLISH_CHORD_NAME = %s

# Default window pos (-1: auto)
WINDOW_X = %s
WINDOW_Y = %s

# Default window size (0: maximized)
WINDOW_WIDTH  = %s
WINDOW_HEIGHT = %s
""" % (self.MIDI_USE_TEMP_FILE, self.MIDI_COMMAND, self.PAGE_FORMAT, self.PAGE_MARGIN_TOP, self.PAGE_MARGIN_BOTTOM, self.PAGE_MARGIN_INTERIOR, self.PAGE_MARGIN_EXTERIOR, self.PREVIEW_COMMAND_PDF, self.NUMBER_OF_UNDO, repr(self.PREVIOUS_FILES), self.DISPLAY_PLAY_BAR, self.ASK_FILENAME_ON_EXPORT, self.LAST_DIR, self.PLAY_AS_TYPING, self.NUMBER_OF_PREVIOUS_FILES, self.AUTOMATIC_DURATION, self.FONTSIZE, self.ENGLISH_CHORD_NAME, self.WINDOW_X, self.WINDOW_Y, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

  def save(self):
    open(CONFIGFILE, "w").write(str(self))

  def edit(self):
    import songwrite3.__editobj3__, editobj3
    
    def on_validate(obj):
      self.MIDI_USE_TEMP_FILE = self.MIDI_COMMAND.find("%s") != -1
      self.save()
      
    editobj3.edit(self, on_validate)
    
    
config = Config()

