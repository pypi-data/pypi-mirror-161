# -*- coding: utf-8 -*-

# Songwrite 3
# Copyright (C) 2016-2016 Jean-Baptiste LAMY -- jibalamy@free.fr
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

import sys, os, atexit

try:
  import getpass
  username = getpass.getuser()
  PIPE = "/tmp/songwrite3_pipe_%s" % username
except:
  PIPE = ""

def is_already_running():
  if (not PIPE) or (not os.path.exists(PIPE)): return False
  return True
  
def create():
  global PIPE
  
  if PIPE:
    try:
      os.mkfifo(PIPE)
    except:
      print("WARNING: Cannot open pipe %s." % PIPE, file = sys.stderr)
    atexit.register(destroy)
    
def destroy():
  if PIPE: os.unlink(PIPE)


THREAD = None
def listen():
  global THREAD # QThread must be kept in memory
  
  import PyQt5.QtCore as qtcore, songwrite3.model as model
  
  class ListeningThread(qtcore.QThread):
    commandReceived = qtcore.pyqtSignal([str])
    def run(self):
      while 1:
        f = open(PIPE, "r")
        command = f.readline()[:-1]
        f.close()
        if command:
          print("Received from pipe:", command, file = sys.stderr)
          self.commandReceived.emit(command)
          
  THREAD = ListeningThread()
  THREAD.commandReceived.connect(on_pipe_command_received)
  THREAD.start()
  
def send(command):
  import threading
  
  class SendingThread(threading.Thread):
    def __init__(self):
      threading.Thread.__init__(self)
      self.done = False
      
    def run(self):
      f = open(PIPE, "w")
      if self.done: return # Timeouted
      f.write(command + "\n")
      f.close()
      self.done = True
      
  thread = SendingThread()
  thread.start()
  thread.join(0.5) # Time out
  if not thread.done:
    thread.done = True # Prevent the thread from writing later
    return False
  else: return True
  
def on_pipe_command_received(command):
  try:
    if   command.startswith("open "):
      import songwrite3.model as model, songwrite3.main as main
      song = model.get_song(command[5:])
      main.App(song)
    elif command.startswith("new "):
      import songwrite3.main as main
      main.App()
    else:
      print("WARNING: Unknown command received!")
      
  except: sys.excepthook(*sys.exc_info())
    
if __name__ == "__main__":
  send("open /home/jiba/audio/tablatures/cours_tristan/tristan_reve.sw.xml")
