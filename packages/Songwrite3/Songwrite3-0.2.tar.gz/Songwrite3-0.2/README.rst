Songwrite 3
===========

A tablature and music score editor
----------------------------------

Songwrite 3 is a music score and songbook editor. This software is
especially designed for musicians who do not master solfege (like me!)
and to Linuxian musicians. Songwrite can edit staffs, but also
tablatures (for guitar, bass, banjo, lyre and diatonic accordion,...)
and flute fingerings (for tin whistle, recorder,...); it also manages
lyrics. Songwrite can play and print the partitions.

Songwrite is a free software (libre software) written in Python. It
is available under GNU GPL.

See the complete doc in ./doc/en/doc.pdf
or the French version in ./doc/fr/doc.pdf

NB: this source tarball does not include the source of the
documentation (in LyX format) ; it can be found in the development
version on Bitbucket.


License
-------

Songwrite is Free Software.
It is available under GNU GPL.


Requirements
------------

 * Python 3.4 or more (older version may work but have not been tested)

 * EditObj 3

 * Qt 5 and PyQt 5

 * Timidity and  Timidity instruments, or Playmidi, or  another way to
   play midi file (require for playing tablature; you can still create
   midi file without)

 * TexLive (PDFLatex) for printing, with the following packages:
   babel, multicol

 * Atril or another PDF viewer


Installation
------------

Untar the tarball.
Then you can immediately run Songwrite 3 by running the ./songwrite3 script.

Songwrite 3 uses Python's DistUtils for installation.
To install, type (as root):

cd Songwrite3-*
python3 ./setup.py install

NB: If you get a warning at the end ("warning: install: modules
installed to '/usr/share/'..."), you can safely ignore it.

You can now run Songwrite 3 by typing "songwrite3" in a console. Songwrite 3 is also added
to the desktop application menu (in the Sound and Video category).

By default, Songwrite 3 is installed in /usr, you can modify the
setup.cfg file if you prefer another location.


Known problems and workarounds
------------------------------

When using Timidity version < 2.14, cracking sounds may appear. A workaround is to set extra command line 
parameters for Timidity in Songwrite 3 Preferences as follows:

::
   
   timidity -idt -Wd -A120 --output-24bit -


Links
-----

Songwrite3 on BitBucket (development repository): https://bitbucket.org/jibalamy/songwrite3

Website: http://www.lesfleursdunormal.fr/static/informatique/songwrite/index_en.html                      

Mail me for any comment, problem, suggestion or help !

Jiba -- Jean-Baptiste LAMY -- jibalamy @ free.fr
