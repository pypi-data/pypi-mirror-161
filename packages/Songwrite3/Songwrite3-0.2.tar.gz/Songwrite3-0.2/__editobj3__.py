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

import os, os.path
from collections import OrderedDict
import editobj3, editobj3.introsp as introsp, editobj3.field as field
import songwrite3.globdef as globdef, songwrite3.model as model

INSTRUMENTS = [i.split(None, 1)[1] for i in _("__instru__").split("\n")]

INSTRUMENTS_2_ID = { instrument : i for (i, instrument) in enumerate(INSTRUMENTS) }

editobj3.TRANSLATOR = _


import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui

import editobj3.field_qt as field_qt, editobj3.editor_qt as editor_qt

editor_qt.SMALL_ICON_SIZE = 48



class QtDurationField(field_qt.QtField, qtwidgets.QWidget):
  def __init__(self, gui, master, obj, attr, undo_stack):
    qtwidgets.QWidget.__init__(self)
    super(QtDurationField, self).__init__(gui, master, obj, attr, undo_stack)
    self.options = []

    toolbar1 = qtwidgets.QToolBar()
    toolbar2 = qtwidgets.QToolBar()
    
    toolbar1.setIconSize(qtcore.QSize(48, 48))
    toolbar2.setIconSize(qtcore.QSize(48, 48))

    radio_group = qtwidgets.QActionGroup(self)
    for i in [1, 2, 3, 4, 5, 6]:
      if i < 3: toolbar = toolbar1
      else:     toolbar = toolbar2
      action = qtwidgets.QAction(toolbar)
      action.setIcon(qtgui.QIcon(os.path.join(globdef.DATADIR, "note_%s.png" % (6 * 2 ** (7 - i)))))
      action.setCheckable(True)
      radio_group.addAction(action)
      self.options.insert(0, action)
      toolbar.addAction(action)
    self.doted   = qtwidgets.QCheckBox(_("Dotted"))
    self.triplet = qtwidgets.QCheckBox(_("Triplet"))

    self.update()

    self.doted  .stateChanged.connect(self.validate)
    self.triplet.stateChanged.connect(self.validate)
    for option in self.options[::-1]: option.toggled.connect(self.validate)

    layout = qtwidgets.QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(toolbar1)
    layout.addWidget(toolbar2)
    layout2 = qtwidgets.QHBoxLayout()
    layout2.addWidget(self.doted)
    layout2.addWidget(self.triplet)
    layout.addLayout(layout2)
    self.setLayout(layout)

  def get_value(self):
    v = field.Field.get_value(self)
    if v is introsp.NonConsistent: return 0
    return v

  def validate(self, *args):
    for i, option in enumerate(self.options):
      if option.isChecked():
        v = 6 * 2 ** (i + 1)
        break
    else: v = 0
    if   self.doted  .isChecked(): v = int(v * 1.5)
    elif self.triplet.isChecked(): v = int(v / 1.5)
    self.set_value(v)

    if not self.updating:
      import songwrite3.main
      if isinstance(self.o, introsp.ObjectPack): partition = self.o.objects[0].partition
      else:                                      partition = self.o.partition
      songwrite3.main.APPS[partition.song].canvas.current_duration = v

  def update(self):
    self.updating += 1
    try:
      v = self.get_value()

      if v in (9, 18, 36, 72, 144, 288, 576):
        v = int(v / 1.5)
        self.doted.setChecked(True)
      else:
        self.doted.setChecked(False)

      if v in (4,  8, 16, 32,  64, 128, 256):
        v = int(v * 1.5)
        self.triplet.setChecked(True)
      else:
        self.triplet.setChecked(False)

      i = { 12 : 0, 24: 1, 48 : 2, 96 : 3, 192 : 4, 384 : 5 }.get(v)
      if not i is None: self.options[i].setChecked(1)
    finally: self.updating -= 1


DurationField  = QtDurationField

        
introsp.def_attr("details"      , field.HiddenField)
introsp.def_attr("icon_filename", field.HiddenField)

descr = introsp.description(globdef.Config)
descr.set_label  (_("Preferences"))
descr.set_details(_("__config_preamble__"))
descr.def_attr("MIDI_COMMAND"        , field.StringField)
descr.def_attr("PREVIEW_COMMAND_PDF" , field.StringField)
descr.def_attr("preview_command_pdf" , field.HiddenField)
descr.def_attr("PREVIEW_COMMAND_PDF2", field.HiddenField)
descr.def_attr("MIDI_USE_TEMP_FILE"  , field.HiddenField)
descr.def_attr("WINDOW_WIDTH"        , field.HiddenField)
descr.def_attr("WINDOW_HEIGHT"       , field.HiddenField)
descr.def_attr("WINDOW_X"            , field.HiddenField)
descr.def_attr("WINDOW_Y"            , field.HiddenField)

descr.def_attr("PAGE_FORMAT"         , field.EnumField({ _("A3") : "a3paper", _("A4") : "a4paper", _("A5") : "a5paper", _("letter") : "letterpaper", _("legal") : "legalpaper" }))
descr.def_attr("PAGE_MARGIN_TOP"     , field.FloatField)
descr.def_attr("PAGE_MARGIN_BOTTOM"  , field.FloatField)
descr.def_attr("PAGE_MARGIN_INTERIOR", field.FloatField)
descr.def_attr("PAGE_MARGIN_EXTERIOR", field.FloatField)

descr.def_attr("PREVIOUS_FILES"          , field.HiddenField)
descr.def_attr("ASK_FILENAME_ON_EXPORT"  , field.BoolField)
descr.def_attr("NUMBER_OF_PREVIOUS_FILES", field.IntField)
descr.def_attr("LAST_DIR"                , field.StringField)

#descr.def_attr("SIDE_BAR_POSITION", field.EnumField(["left", "right", "top", "bottom", "floating_horizontal", "floating_vertical", "none"]))
descr.def_attr("SIDE_BAR_POSITION", field.HiddenField)
descr.def_attr("AUTOMATIC_DURATION", field.BoolField)
descr.def_attr("PLAY_AS_TYPING", field.BoolField)
descr.def_attr("DISPLAY_PLAY_BAR", field.BoolField)
descr.def_attr("FONTSIZE", field.IntField)
descr.def_attr("ENGLISH_CHORD_NAME", field.BoolField)


def ask_new_song_ref(Class, songbook):
  import songwrite3.main as main
  filename = main.APPS[songbook].prompt_open_filename(".sw.xml")
  if not filename: return None
  song_ref = Class(songbook)
  song_ref.set_filename(filename)
  return song_ref

descr = introsp.description(model.Songbook)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "songbook.png"))
descr.def_attr("song_refs", addable_values  = [introsp.NewInstanceOf(model.SongRef)], add_method = "insert_song_ref", remove_method = "remove_song_ref", label = "")
descr.def_attr("title"    , field.StringField)
descr.def_attr("authors"  , field.StringField)
descr.def_attr("comments" , field.TextField)
descr.def_attr("version"  , field.HiddenField)
descr.def_attr("filename" , field.HiddenField)

descr = introsp.description(model.SongRef)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "song.png"))
descr.def_attr("filename", field.FilenameField)
descr.def_attr("title"   , field.HiddenField)
descr.def_attr("songbook", field.HiddenField)
descr.def_attr("song"    , field.HiddenField)
descr.set_constructor(introsp.Constructor(ask_new_song_ref))



def ask_new_partition(song):
  view_types = []
  for category in model.VIEW_CATEGORIES:
    for View in model.VIEWS[category]:
      view_types.append(introsp.NewInstanceOf(View, _(View.__name__), os.path.join(globdef.DATADIR, View.default_icon_filename)))
      
  return view_types
  

import songwrite3.plugins.pdf.pdf_latex

descr = introsp.description(model.Song)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "song.png"))
descr.def_attr("partitions", addable_values = ask_new_partition, add_method = "insert_partition", remove_method = "remove_partition", label = "")
descr.def_attr("title"    , field.StringField)
descr.def_attr("authors"  , field.StringField)
descr.def_attr("copyright", field.StringField)
descr.def_attr("comments" , field.TextField)
descr.def_attr("filename" , field.HiddenField)
descr.def_attr("playlist" , field.HiddenField)
descr.def_attr("version"  , field.HiddenField)
descr.def_attr("mesures"  , field.HiddenField)
descr.def_attr("lang"     , field.EnumField(dict((_("__lang__%s" % code), code) for code in songwrite3.plugins.pdf.pdf_latex.lang_iso2latex.keys()), long_list = 0))
descr.def_attr("print_nb_mesures_per_line", field.RangeField(1, 20))
descr.def_attr("printfontsize", field.RangeField(6, 28))
descr.def_attr("print_with_staff_too", field.BoolField)
descr.def_attr("print_lyrics_columns", field.RangeField(1, 4))

descr = introsp.description(model.View)
descr.set_constructor(introsp.Constructor(lambda View, parent: model.Partition(parent, View.default_instrument, View)))

descr = introsp.description(model.ChorusView)
descr.set_constructor(introsp.Constructor(lambda View, parent: model.Lyrics(parent, header = "Chorus")))

def new_strophe(View, song):
  next_strophe_number = len([lyrics for lyrics in song.partitions if isinstance(lyrics, model.Lyrics) and _("Strophe #%s").replace("%s", "") in lyrics.header]) + 1
  return model.Lyrics(song, header = _("Strophe #%s") % next_strophe_number)
descr = introsp.description(model.StropheView)
descr.set_constructor(introsp.Constructor(new_strophe))

def note_2_base_note_names(note):
  if hasattr(note, "partition"): tonality = note.partition.tonality
  else:                          tonality = "C"
  d = OrderedDict()
  for i in range(12): d[model.note_label(i, False, tonality)] = i
  return d
  


def partition_2_icon_filename(self):
  return os.path.join(globdef.DATADIR, self.view.get_icon_filename())

VIEW_TYPE_NAMES = { _(View.__name__) : View for Views in model.VIEWS.values() for View in Views }

def view_value_2_enum(partition, view_type):
  if hasattr(view_type, "__name__"): return _(view_type.__name__)
  return ""

def view_enum_2_value(partition, view_type_name):
  return VIEW_TYPE_NAMES[view_type_name]

class Tuning(object):
  def __init__(self, strings):
    self.strings = strings
    self._string_class = strings[0].__class__

  def __str__(self): return _("Tuning")
  
  def insert(self, index, string): self.strings.insert(index, string)
    
  def remove(self, string): self.strings.remove(string)

def get_tuning(partition):
  if hasattr(partition.view, "strings"): return Tuning(partition.view.strings)
  return None

def new_tab_string(Class, tuning): return tuning._string_class()

descr = introsp.description(Tuning)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "guitar.png"))
descr.def_attr("strings", addable_values = [introsp.NewInstanceOf(model.TablatureString)], add_method = "insert", remove = "remove", label = "")

def nb_sharp_or_bemol(tonality):
  alterations = model.TONALITIES[tonality]
  if not alterations: return ""
  if alterations[0] is model.DIESES[0]: return "\t(%s ♯)" % len(alterations)
  return "\t(%s ♭)" % len(alterations)

descr = introsp.description(model.Partition)
descr.set_icon_filename(partition_2_icon_filename)
descr.def_attr("header"    , field.TextField)
descr.def_attr("instrument", field.EnumField(INSTRUMENTS_2_ID))
descr.def_attr("tonality"           , field.EnumField({ _("tonality_%s" % tonality) + nb_sharp_or_bemol(tonality) : tonality for tonality in model.TONALITIES.keys() }, translate = False))
descr.def_attr("instrument_tonality", field.EnumField({ _("tonality_%s" % tonality) : tonality for tonality in model.TONALITIES.keys() }, translate = False))
descr.def_attr("view"      , field.HiddenField)
descr.def_attr("song"      , field.HiddenField)
descr.def_attr("notes"     , field.HiddenField)
descr.def_attr("view_type" , field.EnumField(set(VIEW_TYPE_NAMES.keys()), value_2_enum = view_value_2_enum, enum_2_value = view_enum_2_value))
descr.def_attr("capo"      , field.IntField)
descr.def_attr("g_key"     , field.BoolField)
descr.def_attr("f_key"     , field.BoolField)
descr.def_attr("g8"        , field.BoolField)
descr.def_attr("print_with_staff_too", field.BoolField)
descr.def_attr("volume"    , field.RangeField(0, 255))
descr.def_attr("muted"     , field.BoolField)
descr.def_attr("chorus"    , field.RangeField(0, 127))
descr.def_attr("reverb"    , field.RangeField(0, 127))
descr.def_attr("let_ring"  , field.BoolField)
descr.def_attr("visible"   , field.HiddenField, get_method = lambda partition: partition.view.visible, set_method = lambda partition, visible: setattr(partition.view, "visible", visible))
descr.def_attr("tuning"    , field.ObjectSelectorField, get_method = get_tuning)


def string_2_icon_filename(self):
  return os.path.join(globdef.DATADIR, "string_%s.png" % self.width())
  
descr = introsp.description(model.TablatureString)
descr.set_icon_filename(string_2_icon_filename)
descr.def_attr("notation_pos", field.HiddenField)
descr.def_attr("base_note"   , field.HiddenField)
descr.def_attr("octavo"      , field.EnumField(list(range(10))))
descr.def_attr("base_value"  , field.EnumField(note_2_base_note_names, translate = False))
descr.set_constructor(introsp.Constructor(new_tab_string))

#descr = introsp.description(model.DrumString)
#descr.set_icon_filename(os.path.join(globdef.DATADIR, "tamtam.png"))
#descr.def_attr("notation_pos", field.HiddenField)


def note_2_icon_filename(self):
  filename = os.path.join(globdef.DATADIR, "note_%s.png" % self.duration)
  if os.path.exists(filename): return filename
  return os.path.join(globdef.DATADIR, "note_96.png")


descr = introsp.description(model.Note)
descr.set_icon_filename(note_2_icon_filename)
descr.def_attr("string_id"   , field.HiddenField)
descr.def_attr("time"        , field.HiddenField)
descr.def_attr("partition"   , field.HiddenField)
descr.def_attr("button_rank" , field.HiddenField)
descr.def_attr("bellows_dir" , field.HiddenField)
descr.def_attr("duration"    , DurationField)
descr.def_attr("value"       , field.HiddenField)
descr.def_attr("base_value"  , field.EnumField(note_2_base_note_names, translate = False))
descr.def_attr("octavo"      , field.EnumField(list(range(10))))
descr.def_attr("fx"          , field.EnumField(dict((_(fx or "(none)"), fx) for fx in model.FXS          )), optional = False)
descr.def_attr("link_fx"     , field.EnumField(dict((_(fx or "(none)"), fx) for fx in model.LINK_FXS     )), optional = False)
descr.def_attr("duration_fx" , field.EnumField(dict((_(fx or "(none)"), fx) for fx in model.DURATION_FXS )), optional = False)
descr.def_attr("strum_dir_fx", field.EnumField(dict((_(fx or "(none)"), fx) for fx in model.STRUM_DIR_FXS)), optional = False)
descr.def_attr("volume"      , field.RangeField(0, 255))

descr = introsp.description(model.Mesure)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "bar.png"))
descr.def_attr("number"   , field.HiddenField)
descr.def_attr("time"     , field.HiddenField)
descr.def_attr("duration" , field.HiddenField)
descr.def_attr("song"     , field.HiddenField)
descr.def_attr("rythm1"   , field.EnumField([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
descr.def_attr("rythm2"   , field.EnumField([4, 8]))
descr.def_attr("tempo"    , field.IntField)
descr.def_attr("syncope"  , field.BoolField)

def new_playlist_item(Class, playlist):
  import songwrite3.main as main
  app = main.APPS[playlist.song]
  mesure = app.selected_mesure
  if isinstance(mesure, model.Mesure): start = end = mesure.get_number()
  else:
    mesure_numbers = [mesure.get_number() for mesure in mesure.objects]
    start = min(mesure_numbers)
    end   = max(mesure_numbers)
  return Class(playlist, start, end)

descr = introsp.description(model.Playlist)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "playlist.png"))
descr.def_attr("playlist_items", addable_values = [introsp.NewInstanceOf(model.PlaylistItem)], add_method = "insert", remove_method = "remove", label = "")
descr.def_attr("symbols"       , field.HiddenField)
descr.def_attr("song"          , field.HiddenField)

descr = introsp.description(model.PlaylistItem)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "playlist.png"))
descr.def_attr("playlist"    , field.HiddenField)
descr.def_attr("from_mesure" , field.HiddenField)
descr.def_attr("to_mesure"   , field.HiddenField)
descr.def_attr("from_mesure1", field.IntField)
descr.def_attr("to_mesure1"  , field.IntField)
descr.set_constructor(introsp.Constructor(new_playlist_item))

descr = introsp.description(model.Lyrics)
descr.set_icon_filename(os.path.join(globdef.DATADIR, "lyrics.png"))
descr.def_attr("text"  , field.HiddenField)
descr.def_attr("melody", field.HiddenField)
descr.def_attr("song"  , field.HiddenField)
descr.def_attr("header", field.TextField)
descr.def_attr("show_all_lines_on_melody"  , field.BoolField)
descr.def_attr("show_all_lines_after_score", field.BoolField)
