#!/usr/bin/env python

#debian-section: web

from distutils.core import setup, Extension

if __name__=='__main__':
    setup(name="toursst",
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
	  licence="GNU GPL",

	  packages=[
	"TouRSSt",
	"TouRSSt.format",
	"TouRSSt.format.email",
	"TouRSSt.writer",
	],
	  scripts=[
	"toursst",
	],
          data_files=[('lib/python2.2/site-packages/TouRSSt',
                       ["TouRSSt/plugins.tml"])],
	  )
