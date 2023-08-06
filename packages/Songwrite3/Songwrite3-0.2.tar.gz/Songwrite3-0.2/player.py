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

import sys, subprocess, os, fcntl
from io import BytesIO

import PyQt5.QtCore as qtcore

import editobj3
import songwrite3, songwrite3.globdef as globdef

_p            = None
_midi         = ""
_loop         = 0
_tracker      = None
_last_tracker = None
_output       = b""

def is_playing(): return _p and (_p.poll() is None)

def stop():
  global _p, _tracker
  if not _p is None:
    if _tracker:
      _tracker(-1)
      _tracker = None
      
    try:
      _p.terminate()
      _p.kill()
    except OSError:
      sys.excepthook(*sys.exc_info())
    _p  = None
    
def play(midi, loop = 0, tracker = None):
  global _p, _midi, _loop, _tracker, _last_tracker, _output
  
  stop()
  
  if not globdef.config.DISPLAY_PLAY_BAR: tracker = None
  _midi    = midi
  _loop    = loop
  _tracker = _last_tracker = tracker
  _output  = b""
  
  _play()
  
def _play():
  global _p, _midi, _loop, _tracker
  if globdef.config.MIDI_USE_TEMP_FILE:
    import tempfile
    file = tempfile.mktemp(".midi")
    open(file, "w").write(_midi)
    _p = p = subprocess.Popen(globdef.config.MIDI_COMMAND % file, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
  else:
    _p = p = subprocess.Popen(globdef.config.MIDI_COMMAND, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    _p.stdin.write(_midi)
    _p.stdin.close()
  fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
  
  
  try: _play.qt_timer.stop()
  except: pass
  _play.qt_timer = qtcore.QTimer()
  _play.qt_timer.timeout.connect(on_timer)
  _play.qt_timer.setSingleShot(False)
  if _tracker: _play.qt_timer.setInterval( 50)
  else:        _play.qt_timer.setInterval(300)
  _play.qt_timer.start()
  

def on_timer():
  global _tracker, _output
  
  try:
    if _p is None:
      _play.qt_timer.stop() #return 0 # Stop was called
      return
    
    r = _p.poll()
    
    if r is None:
      if _tracker:
        output = _p.stdout.read()
        
        if output:
          lines   = (_output + output).split(b"\n")
          _output = lines[-1]
          if len(lines) > 1:
            line = lines[-2]
            try:
              if b":" in line: t = int(line[line.rfind(b":") + 3 :])
              else:            t = int(line)
            except: return # 1
            _tracker(t)
            if t == -1:
              _tracker = None # Tracking has reached its end !
              stop()
              if _loop:
                _tracker = _last_tracker
                _play()
                
    else:
      _play.qt_timer.stop()
      
      if (r == 0) and _loop:
        _tracker = _last_tracker
        _play()
        
  except: sys.excepthook(*sys.exc_info())


noteplayer = None

def play_note(instrument, value):
  if not globdef.config.PLAY_AS_TYPING: return
  
  stop()
  
  global noteplayer
  if not noteplayer:
    noteplayer = songwrite3.model.Song()
    noteplayer.partitions.append(songwrite3.model.Partition(noteplayer))
    noteplayer.partitions[0].notes.append(songwrite3.model.Note(noteplayer.partitions[0], 0, 48, 0))
  noteplayer.partitions[0].instrument = instrument
  noteplayer.partitions[0].notes[0].value = value
  
  play(songwrite3.midi.song_2_midi(noteplayer))
