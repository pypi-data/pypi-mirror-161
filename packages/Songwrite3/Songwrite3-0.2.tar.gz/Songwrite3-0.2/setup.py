#! /usr/bin/env python

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

import os, os.path, sys
import setuptools

HERE = os.path.dirname(sys.argv[0]) or "."

def do(command):
  print(command, file = sys.stderr)
  os.system(command)


package_data = {"songwrite3" : ["data/*",
                                "manpage/*", "manpage/man1/*",
                                "locale/*", "locale/en/*", "locale/en/LC_MESSAGES/*", "locale/fr/*", "locale/fr/LC_MESSAGES/*",
                                "doc/*", "doc/en/*", "doc/fr/*",
]}
  
if "--no-xdg" in sys.argv:
  sys.argv.remove("--no-xdg")
  no_xdg = 1
else:
  no_xdg = 0

if ("uninstall" in sys.argv) or ("uninstall-xdg" in sys.argv):
  print(file = sys.stderr)
  print("XDG un-installation (application, MIME type and icons)...", file = sys.stderr)
  do("xdg-mime uninstall %s/application-x-songwrite.xml" % HERE)
  do("xdg-icon-resource uninstall --novendor --context apps --noupdate --size 32 songwrite3" % HERE)
  do("xdg-icon-resource uninstall --novendor --context apps --noupdate --size 64 songwrite3" % HERE)
  do("xdg-desktop-menu uninstall --novendor %s/songwrite3.desktop" % HERE)
  sys.argv.remove("uninstall-xdg")

#data_files = [
#  (os.path.join("songwrite3", "data"),
#  [os.path.join("data", file) for file in os.listdir("data") if (file != "CVS") and (file != ".hg") and (file != ".svn") and (file != ".arch-ids")]),
#  (os.path.join("man", "man1"),
#  [os.path.join("manpage", "man1", "songwrite3")]),
#  ]
#if not no_lang:
#  data_files = data_files + [
#    (os.path.join(os.path.dirname(mo_file)), [mo_file])
#    for mo_file
#    in  glob.glob(os.path.join(".", "locale", "*", "LC_MESSAGES", "*"))
#    ]
#
#for doc_lang in ["fr", "en"]:
#  data_files.append(
#    (os.path.join("doc", "songwrite3", doc_lang),
#     glob.glob(os.path.join(".", "doc", doc_lang, "doc.pdf"))),
#    )

#distutils.core.setup(
setuptools.setup(
  name         = "Songwrite3",
  version      = "0.2",
  license      = "GPL",
  description  = "Tablature editor with Python 3, Qt 5, EditObj 3, and Timidity",
  author       = "Lamy Jean-Baptiste",
  author_email = "jibalamy@free.fr",
  url          = "http://www.lesfleursdunormal.fr/static/informatique/songwrite/index_en.html",
  
  package_dir  = {"songwrite3" : "."},
  packages     = ["songwrite3",
                  "songwrite3.plugins",
                  "songwrite3.plugins.abc",
                  "songwrite3.plugins.additional_instruments",
                  "songwrite3.plugins.fingering",
                  "songwrite3.plugins.lyre",
                  "songwrite3.plugins.midi",
                  "songwrite3.plugins.pdf",
                  "songwrite3.plugins.songwrite",
                  "songwrite3.plugins.texttab",
                  "songwrite3.plugins.chord",
                  "songwrite3.plugins.accordion",
  ],
  
  install_requires = ["Editobj3"], # XXX PyQt5 not supported here, but it IS required
  
  scripts      = ["songwrite3"],
  platforms    = ["Unix", "Linux"],
  
  classifiers  = [
    "Development Status :: 4 - Beta",
    "Environment :: X11 Applications",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Natural Language :: French",
    "Natural Language :: English",
    "Operating System :: Unix",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.5",
    "Topic :: Artistic Software",
    "Topic :: Multimedia :: Sound/Audio",
    "Topic :: Multimedia :: Sound/Audio :: Editors",
    "Topic :: Multimedia :: Sound/Audio :: MIDI",
    ],
  
  package_data = package_data,
)


if ("install" in sys.argv) and (not no_xdg):
  print(file = sys.stderr)
  print("XDG installation (application, MIME type and icons)...", file = sys.stderr)
  do("xdg-mime install %s/application-x-songwrite.xml" % HERE)
  do("xdg-icon-resource install --novendor --context apps      --noupdate --size 32 %s/data/songwrite3_32x32.png songwrite3" % HERE)
  do("xdg-icon-resource install --novendor --context apps                 --size 64 %s/data/songwrite3_64x64.png songwrite3" % HERE)
  #do("xdg-icon-resource install            --context mimetypes --noupdate --size 32 %s/data/songwrite3_32x32.png application-x-songwrite" % HERE)
  #do("xdg-icon-resource install            --context mimetypes            --size 64 %s/data/songwrite3_64x64.png application-x-songwrite" % HERE)
  do("xdg-desktop-menu install  --novendor %s/songwrite3.desktop" % HERE)
