#!/usr/bin/env python

#debian-section: web

import os.path
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib

def version():
    header = file('debian/changelog').readline()
    source, version, dummy = header.split(None, 2)
    if version.startswith('(') and version.endswith(')'):
        return version[1:-1]
    else:
        return None

if __name__=='__main__':
    setup(name="toursst",
          version=version(),
	  description="RSS channel news items where you want them",
	  long_description="""

TouRSSt tours the web so you don't have to. Run frequently, it pulls
new RSS news items from a number of channels and puts them where you
want.

Currently it can deliver news items to a Maildir, but future additions
will include sending over SMTP, perhaps writing out aggregated RSS
feeds, and so on. TouRSSt is built to be reasonably modular, so you
should have no problems adding your own delivery plugin, if you just
know a bit of Python.

""".strip(),
	  author="Tommi Virtanen",
	  author_email="tv@debian.org",
	  url="http://toursst.sourceforge.net/",
	  license="GNU GPL",
          platforms = ["any"],

          classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: DFSG approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Office/Business :: News/Diary',
        ],

	  packages=[
	"TouRSSt",
	"TouRSSt.format",
	"TouRSSt.format.email",
	"TouRSSt.writer",
	],
	  scripts=[
	"toursst",
	],
          data_files=[(os.path.join(get_python_lib(), 'TouRSSt'),
                       ["TouRSSt/plugins.tml"])],
	  )
