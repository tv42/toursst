import MimeWriter
import cStringIO
import urllib
import time

from TouRSSt.format.email import simple

class TouRSStFormatterEmailMIME(simple.TouRSStFormatterEmailSimple):
    """Format an RSS item and article for email"""

    def __init__(self):
        simple.TouRSStFormatterEmailSimple.__init__(self)
        
    def format(self, item, feed):
        date=time.time() #TODO
        out=cStringIO.StringIO()
        m=MimeWriter.MimeWriter(out)
        for key, val in self._headers(item, feed, date):
            if key!='content-type':
                m.addheader(key, val)

	m.addheader('Mime-Version', '1.0')
        m.startmultipartbody('mixed')

        subwriter=m.nextpart()
        b=subwriter.startbody('text/plain')
        b.write(self._body(item, feed, date))

        subwriter=m.nextpart()
	subwriter.addheader('Content-Disposition',
                            'attachment')
	f=urllib.urlopen(item.link)
        i=f.info()
        if i:
            for key, val in i.items():
                if key!='content-type':
                    subwriter.addheader(key, val)

        plist=[]
        if i:
            for key in i.getparamnames():
                val=i.getparam(key)
                plist.append((key, val))
        b=subwriter.startbody(i.gettype(), plist)
        r=f.read()
        while r:
            b.write(r)
            r=f.read()

        m.lastpart()
        r=out.getvalue()
        out.close()
        return r
