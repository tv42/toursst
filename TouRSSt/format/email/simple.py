"""
Format an RSS item for email.
"""

import cStringIO
import htmllib
import formatter
import string
import time
import os
import itertools

from TouRSSt.format.email import base

starttime=int(time.time())
counter = itertools.count(1)

forbidden = {'description': 1}

class TouRSStDescFormatter(htmllib.HTMLParser):
    pass

def textify(s):
    if s==None:
        return ''
    file=cStringIO.StringIO()
    p=TouRSStDescFormatter(
        formatter.AbstractFormatter(formatter.DumbWriter(file)))
    p.feed(s)
    p.close()
    r=file.getvalue()
    file.close()
    return r

class TouRSStFormatterEmailSimple(base.TouRSStFormatterEmailBase):
    """Format an RSS item for email"""
    
    def __init__(self):
        base.TouRSStFormatterEmailBase.__init__(self)

    def _msgid(self):
        import socket
        return 'toursst.%i.%i.%s@%s'\
               %(os.getpid(), starttime, next(counter),
                 socket.gethostbyaddr(socket.gethostname())[0])

    def _headers(self, item, feed, date):
        info=[('X-TouRSSt', 'Extra info disabled')] #TODO

        return [('Date', time.strftime("%a, %d %b %Y %H:%M:%S %z", time.gmtime(date))),
                ('From', string.strip(feed.title)+' <nobody@invalid>'),
                ('Subject', item.getTitle()),
                ('Message-Id', ' <'+self._msgid()+'>')]+info

    def _body(self, item, feed, date):
        channel=string.ljust(feed.title, 50)
        if len(channel)>50:
            channel=string.rstrip(channel)+'\n'+string.ljust(' ', 50)

        desc=None
        try:
            desc=item.description
        except AttributeError:
            try:
                desc=item.getDescription()
            except KeyError:
                pass
       
        s=\
            item.getTitle()+'\n'+\
            string.rjust(time.strftime("%a %H:%M %d/%m/%Y",
                                       time.gmtime(date)),
                         70)+'\n'+\
            '\n'+\
            item.getURL()+'\n'+\
            '\n'+\
            textify(desc)+'\n'
        return s

    def format(self, item, feed):
        date=time.time() #TODO
        return string.join(
            map(lambda keyval: string.join(keyval, ': '),
                self._headers(item, feed, date)),
            '\n')+'\n'+'\n'+self._body(item, feed, date)


#        info=string.join(map(lambda tuple: "X-TouRSSt-%s: %s"%tuple,
#                             filter(lambda x: not forbidden.has_key(x[0]),
#                                    self.data.items())), "\n")

toursstFormatter = TouRSStFormatterEmailSimple
