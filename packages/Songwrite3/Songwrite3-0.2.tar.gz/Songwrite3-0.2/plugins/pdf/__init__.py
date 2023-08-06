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

import sys, os, atexit

import songwrite3.plugins as plugins
import songwrite3.model   as model
import songwrite3.globdef as globdef


PREVIEW_TMP_FILE = ""

def remove_preview_tmp_file():
  global PREVIEW_TMP_FILE
  if PREVIEW_TMP_FILE:
    os.unlink(PREVIEW_TMP_FILE)
    PREVIEW_TMP_FILE = ""
atexit.register(remove_preview_tmp_file)


class ExportPluginPDF(plugins.ExportPlugin):
  def __init__(self):
    plugins.ExportPlugin.__init__(self, "PDF", [".pdf"], 1, 1)
    
  def export_to_string(self, song):
    import songwrite3.plugins.pdf.pdf_latex as pdf_latex
    return pdf_latex.pdfy(song)
  
  def print_preview(self, song):
    import songwrite3.plugins.pdf.pdf_latex as pdf_latex
    global PREVIEW_TMP_FILE
    
    if PREVIEW_TMP_FILE: remove_preview_tmp_file()
    
    pdf = pdf_latex.pdfy(song)
    
    import subprocess

    pdf_command = globdef.config.get_preview_command_pdf()
    if "%s" in pdf_command:
      import tempfile
      fid, PREVIEW_TMP_FILE = tempfile.mkstemp(suffix = ".pdf", text = 0)
      with open(PREVIEW_TMP_FILE, "wb") as f: f.write(pdf)
      command = pdf_command % PREVIEW_TMP_FILE
      print("Running '%s'" % command, file = sys.stderr)
      p = subprocess.Popen(command, shell = True, close_fds = True)
    else:
      print("Running '%s'" % pdf_command, file = sys.stderr)
      p = subprocess.Popen(pdf_command, shell = True, stdin = subprocess.PIPE, close_fds = True)
      p.stdin.write(pdf)
      p.stdin.close()
      
ExportPluginPDF()
