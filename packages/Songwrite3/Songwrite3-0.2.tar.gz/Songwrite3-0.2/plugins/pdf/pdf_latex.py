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

import sys, os, tempfile, shutil
from io import StringIO

import songwrite3.globdef  as globdef
import songwrite3.model    as model
import songwrite3.plugins  as plugins

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui

def escape_latex(s):
  return s.replace("°", "\\symbol{6}").replace("#", "\\#").replace("_", "\\_").replace("~", "\\~").replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("^", "\\^")

lang_iso2latex = { # Languages supported by LaTeX with Babel
  "" : "\\usepackage[]{babel}",
  }
lang_iso2latex = { # Languages supported by LaTeX with Babel
  "ar" : "arabic",
  "hy" : "armenian",
  "eu" : "basque",
  "bg" : "bulgarian",
  "ca" : "catalan",
  "hr" : "croatian",
  "cs" : "czech",
  "da" : "danish",
  "nl" : "dutch",
  "en" : "english",
  "eo" : "esperanto",
  "et" : "estonian",
  "fa" : "farsi",
  "fi" : "finnish",
  "fr" : "french",
  "gl" : "galician",
  "de" : "german",
  "el" : "greek",
  "hu" : "hungarian",
  "is" : "icelandic",
  "as" : "assamese",
  "bn" : "bengali",
  "gu" : "gujarati",
  "hi" : "hindi",
  "kn" : "kannada",
  "ml" : "malayalam",
  "mr" : "marathi",
  "or" : "oriya",
  "pa" : "panjabi",
  "ta" : "tamil",
  "te" : "telugu",
  "id" : "indonesian",
  "ia" : "interlingua",
  "ga" : "irish",
  "it" : "italian",
  "ku" : "kurmanji",
  "lo" : "lao",
  "la" : "latin",
  "lv" : "latvian",
  "lt" : "lithuanian",
  "mn" : "mongolian",
  "nb" : "bokmal",
  "nn" : "nynorsk",
  "pl" : "polish",
  "pt" : "portuguese",
  "ro" : "romanian",
  "ru" : "russian",
  "sa" : "sanskrit",
  "sr" : "serbian",
  "sk" : "slovak",
  "sl" : "slovenian",
  "es" : "spanish",
  "sv" : "swedish",
  "tr" : "turkish",
  "tk" : "turkmen",
  "uk" : "ukrainian",
  "cy" : "welsh",
  "--" : "",
  }

def latexify_songbook(tmp_dir, songbook):
  latexes = []
  lang    = None
  
  for song_ref in songbook.song_refs:
    song = song_ref.get_song()
    latexes.append(latexify_song(tmp_dir, song, 1))
    if not lang: lang = song.lang

  lang_latex = lang_iso2latex[lang]
  babel_code = "\\usepackage[%s]{babel}" % lang_latex
  open(os.path.join(tmp_dir, "main.latex"), "w").write(("""
\\documentclass[%s,twoside,10pt]{article}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage[lmargin=%scm,rmargin=%scm,tmargin=%scm,bmargin=%scm]{geometry}
\\usepackage{graphicx}
\\usepackage{lmodern,aecompl}
\\usepackage{multicol} 
%s

\\begin{document}

\\sloppy

\\title {%s}
\\author{%s}
\\date  {}
\\maketitle
\\vfill
%s
\\begin{multicols}{2}
\\tableofcontents
\\end{multicols}
\\pagebreak

%s


\\end{document}
""" % (globdef.config.PAGE_FORMAT,
       globdef.config.PAGE_MARGIN_INTERIOR,
       globdef.config.PAGE_MARGIN_EXTERIOR,
       globdef.config.PAGE_MARGIN_TOP,
       globdef.config.PAGE_MARGIN_BOTTOM,
       babel_code,
       escape_latex(songbook.title),
       escape_latex(songbook.authors),
       escape_latex(songbook.comments),
       """
\\newpage
""".join(latexes),
       )))


PDF_ID = 0
def latexify_song(tmp_dir, song, songbook = 0):
  global PDF_ID
  from songwrite3.plugins.pdf.pdf_canvas import BaseCanvas, PDFCanvas
  
  song.remove_unused_mesures()
  
  latex = StringIO()
  
  partitions = song.partitions
  
  lang = lang_iso2latex.get(song.lang, None)
  if lang: babel_code = "\\usepackage[%s]{babel}" % lang
  else:    babel_code = ""
  
  if songbook:
    latex.write("""
\\addcontentsline{toc}{subsection}{%s}

""" % escape_latex(song.title))
    
  else:
    latex.write("""
\\documentclass[%s,twoside,10pt]{article}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage[lmargin=%scm,rmargin=%scm,tmargin=%scm,bmargin=%scm,headheight=0cm,headsep=0cm]{geometry}
\\usepackage{graphicx}
\\usepackage{aecompl}""" % (globdef.config.PAGE_FORMAT,
       globdef.config.PAGE_MARGIN_INTERIOR,
       globdef.config.PAGE_MARGIN_EXTERIOR,
       globdef.config.PAGE_MARGIN_TOP,
       globdef.config.PAGE_MARGIN_BOTTOM,
       ))
    if song.print_lyrics_columns > 1: latex.write("""\\usepackage{multicol}""")
    latex.write("""
%s
\\setlength{\\topskip}{0pt}

\\begin{document}

\\sloppy

""" % babel_code)

  if song.title:
    latex.write("""
\\begin{center}\\begin{LARGE} %s \\end{LARGE}\\end{center}
""" % escape_latex(song.title))
    
  date = song.date()
  if song.authors or date:
    if   not date:         authors_date = song.authors
    elif not song.authors: authors_date = date
    else:                  authors_date = "%s (%s)" % (song.authors, date)
    latex.write("""
\\begin{center}\\begin{large} %s \\end{large}\\end{center}
""" % escape_latex(authors_date))
    
  if song.comments:
    latex.write("""
%s
""" % escape_latex(song.comments).replace("\\n", "\\n\\n"))

  max_time = max([10] + [partition.end_time() for partition in song.partitions if isinstance(partition, model.Partition)])
  max_width = {
    "a3paper"    : 29.7,
    "a4paper"    : 21.0,
    "a5paper"    : 14.8,
    "letterpaper": 21.6,
    "legalpaper" : 21.6,
    }[globdef.config.PAGE_FORMAT] - (globdef.config.PAGE_MARGIN_INTERIOR + globdef.config.PAGE_MARGIN_EXTERIOR)
  max_width = int(round(max_width * 56.8421052631579))
  
  max_mesures_width = 0
  mesuress = []
  selected_mesures = []
  canvas = PDFCanvas(song)
  #canvas.set_default_font_size(song.printfontsize)
  canvas.update_mesure_size()
  width = canvas.start_x
  
  zoom = (max_width - canvas.start_x - 1) / float(song.mesures[min(song.print_nb_mesures_per_line, len(song.mesures)) - 1].end_time() )
  for mesure in song.mesures:
    if len(selected_mesures) >= song.print_nb_mesures_per_line:
      mesuress.append(selected_mesures)
      selected_mesures = []
    selected_mesures.append(mesure)
  if selected_mesures:
    if mesuress and (len(selected_mesures) == 1) and (song.print_nb_mesures_per_line > 3):
      mesuress[-1].append(selected_mesures[0])
    else:
      mesuress.append(selected_mesures)
      
  def mesure_2_repeat(mesure):
    start_repeat = end_repeat = 0
    for symbol in song.playlist.symbols.get(mesure) or []:
      if   symbol.startswith(r"\repeat"):    start_repeat = 1
      elif symbol == r"} % end alternative": end_repeat   = 1
      elif symbol == r"} % end repeat":      end_repeat   = 1
    return start_repeat, end_repeat
    
  def mesures_2_x_width_zoom(mesures, is_last, previous_mesures, previous_zoom):
    if mesures[0] is song.mesures[0]:
      x   = 0
      dx  = 0
      start_repeat, end_repeat = mesure_2_repeat(mesures[0])
      if start_repeat:                  x +=0.3 * canvas.scale; dx -=0.3 * canvas.scale
    else:
      x   = canvas.time_2_x(mesures[0].time) - canvas.start_x
      dx  = x  - mesures[ 0].time
      
      start_repeat, end_repeat = mesure_2_repeat(mesures[0])
      if   start_repeat and end_repeat: x -= 17 * canvas.scale; dx -= 17 * canvas.scale
      elif start_repeat:                x -= 16 * canvas.scale; dx -= 16 * canvas.scale
      elif end_repeat:                  x -=  2 * canvas.scale; dx -=  2 * canvas.scale
      else:                             x -=  2 * canvas.scale; dx -=  2 * canvas.scale
      
    x2    = canvas.time_2_x(mesures[-1].end_time()) - canvas.start_x
    dx2   = x2 - mesures[-1].end_time()
    
    try:    next_mesure = song.mesures[mesures[-1].get_number() + 1]
    except: next_mesure = None
    start_repeat, end_repeat = mesure_2_repeat(next_mesure)
    if   start_repeat and end_repeat: x2 -= 15 * canvas.scale; dx2 -= 15 * canvas.scale
    elif start_repeat:                x2 -= 16 * canvas.scale; dx2 -= 16 * canvas.scale
    elif end_repeat:                  x2 -=  2 * canvas.scale; dx2 -=  2 * canvas.scale
    else:                             x2 -=1.1 * canvas.scale; dx2 -=1.1 * canvas.scale
    
    if is_last and not (len(mesures) < len(previous_mesures)):
      x2 +=  5 * canvas.scale; dx2 +=  5 * canvas.scale
      
    width = x2 - x
    
    if is_last and (len(mesures) < len(previous_mesures)):
      zoom = previous_zoom
      width = (dx2 - dx) + (width - (dx2 - dx)) * zoom + canvas.start_x
      if not end_repeat: width += 5 * canvas.scale
    else:
      zoom  = (max_width - canvas.start_x - (dx2 - dx)) / float(width - (dx2 - dx))
      width = max_width
      
    x = dx + (x - dx) * zoom
    return x, width, zoom

  # We need a second canvas; the first one is only for computation
  pdf_canvas = PDFCanvas(song)
  
  latex.write("""
\\begin{flushleft}
""")
  previous_mesures = []
  previous_zoom    = 0.0
  for mesures in mesuress:
    x, width, zoom = mesures_2_x_width_zoom(mesures, mesures is mesuress[-1], previous_mesures, previous_zoom)
    
    pdf_filename = os.path.join(tmp_dir, "pdf_file_%s.pdf" % PDF_ID)
    pdf_canvas.render(pdf_filename, x, width, mesures[0].time, mesures[-1].end_time(), zoom)
    previous_mesures = mesures
    previous_zoom    = zoom

    if hasattr(qtgui, "QPageLayout"): # setResolution is used for changing resolution.
      latex.write("""
      \\noindent\\includegraphics[clip,scale=0.5]{pdf_file_%s.pdf}\\par""" % PDF_ID)
    else:
      latex.write("""
      \\noindent\\includegraphics[clip,scale=8.3333]{pdf_file_%s.pdf}\\par""" % PDF_ID)
    if mesures is mesuress[-1]: latex.write("""\n""")
    else:                       latex.write("""\\bigskip\n""")
    PDF_ID += 1
    
  latex.write("""
\\end{flushleft}
""")
  latex.write("""
\\vfill
""")
  if song.print_lyrics_columns > 1:
    latex.write("""
\\begin{multicols}{%s}
""" % song.print_lyrics_columns)
  

  first = 1
  for partition in partitions:
    if isinstance(partition, model.Lyrics):
      if not partition.show_all_lines_after_score: continue
      if first:
        first = 0
        #latex.write("""\\noindent """)
      else:
        #if song.print_lyrics_columns > 1:
          latex.write("""
\\smallskip{}

""")
        #else:
        #  latex.write("""\\\\
#\\noindent """)
      if partition.header:
        latex.write("""\\textbf{%s}\\nopagebreak[4]\\\\%%
""" % escape_latex(partition.header))
      else:
        latex.write("""\\noindent """)
        


      text = partition.text.replace("_-\t", "").replace("_\t", " ").replace("-\t", "").replace("\t", " ").replace("_", "").replace(" ,", ",").replace(" ,", ",")
      if text.endswith("\\"): text = text[:-2] # Remove last breakline
      latex.write(escape_latex(text))
      
  if song.print_lyrics_columns > 1:
    latex.write("""
\end{multicols} 
""")
#  else:
#    latex.write("""
#\\vfill
#""")
    
    
  if not songbook:
    latex.write("""
\\end{document}
""")

  if songbook:
    return latex.getvalue()
  else:
    open(os.path.join(tmp_dir, "main.latex"), "w").write(latex.getvalue())


PDF_PAGE_FORMATS = {
  "a3paper"     : "a3",
  "a4paper"     : "a4",
  "a5paper"     : "a5",
  "letterpaper" : "letter",
  "legalpaper"  : "legal",
  }

def do(command):
  print(file = sys.stderr)
  print("Running '%s'..." % command, file = sys.stderr)
  os.system(command)
  
def pdfy(song):
  tmp_dir = tempfile.mkdtemp()
  print(file = sys.stderr)
  print("Using temporary directory '%s'..." % tmp_dir, file = sys.stderr)
  
  if isinstance(song, model.Songbook):
    latexify_songbook(tmp_dir, song)
  else:
    latexify_song    (tmp_dir, song)
    
  do("cd %s; pdflatex -interaction=nonstopmode main.latex" % tmp_dir)
  do("cd %s; pdflatex -interaction=nonstopmode main.latex" % tmp_dir) # For table of content
  
  with open(os.path.join(tmp_dir, "main.pdf"), "rb") as f: r = f.read()
  shutil.rmtree(tmp_dir)
  return r

