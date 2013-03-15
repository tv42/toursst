# -*- test-case-name: TouRSSt.tests.test_rssparser -*-

import time
import string
import socket
import sha
import errno
import os
import os.path

from twisted.internet import reactor, defer
from twisted.web import microdom, client, domhelpers

from TouRSSt import log

class TouRSStItem:
    def __init__(self, dom, fetchtime):
        self.dom=dom
        self.fetchtime=fetchtime

    def getURL(self):
        l = domhelpers.findNodesNamed(self.dom, 'link')
        if l:
            return domhelpers.getNodeText(l[0])
        else:
            return None

    def getTitle(self):
        l = domhelpers.findNodesNamed(self.dom, 'title')
        if l:
            return domhelpers.getNodeText(l[0])
        else:
            return None

    def getDescription(self):
        # http://purl.org/dc/elements/1.1/ description
        l = domhelpers.findNodesNamed(self.dom, 'description')
        if l:
            return domhelpers.getNodeText(l[0])
        else:
            return None

    def hash(self):
        return sha.new(self.getURL()).hexdigest()

def mkdir_if_missing(dir):
    try:
        os.mkdir(dir)
    except OSError, (err, errstr):
        if err!=errno.EEXIST:
            raise

def makeBlocking(d):
    succ, fail = [], []
    d.addCallback(succ.append)
    d.addErrback(fail.append)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    if succ:
        return succ[0]
    else:
        if not fail:
            # it seems the errback above is not called
            # when user presses control-C. Oh well.
            raise KeyboardInterrupt
        raise fail[0].value

class RSSParser:
    def __init__(self, dom, starttime):
        self.dom = dom
        self.starttime = starttime

    updateperiods = {
        'hourly': 60*60,
        'daily': 60*60*24,
        'weekly': 60*60*24*7,
        'monthly': 60*60*24*30,
        'yearly': 60*60*24*365,
        }

    def get_update_period(self):
        return self.updateperiods['hourly'] #TODO

        period='daily'
        freq=1
        try:
            pass #TODO period=rss[('http://purl.org/rss/1.0/modules/syndication/', 'updatePeriod')]
        except KeyError:
            pass
        
        try:
            pass #TODO freq=int(rss[('http://purl.org/rss/1.0/modules/syndication/', 'updateFrequency')])
        except KeyError:
            pass
        
        return self.updateperiods[period]/freq

    def getTitle(self):
        l = domhelpers.findNodesNamed(self.dom, 'title')
        if l:
            return domhelpers.getNodeText(l[0])
        else:
            return None

    def getDescription(self):
        l = domhelpers.findNodesNamed(self.dom, 'description')
        if l:
            return domhelpers.getNodeText(l[0])
        else:
            return None

    def getURL(self):
        l = domhelpers.findNodesNamed(self.dom, 'link')
        if l:
            return domhelpers.getNodeText(l[0])
        else:
            return None

    def getItems(self):
        l=[]
        for dom in domhelpers.findNodesNamed(self.dom, 'item'):
            l.append(TouRSStItem(dom, self.starttime))
        return l

class TouRSStFeedURLChangedException(Exception):
    """That's not the same URL!"""
    def __init__(self, oldURL, newURL):
        Exception.__init__(self)
        self.oldURL=oldURL
        self.newURL=newURL

    def __str__(self):
        return 'Feed has changed URL or two feeds hash into one. Old URL was %r, new is %r.' % (self.oldURL, self.newURL)

class TouRSStFeed:
    #identification:
    #  feedurl
    #internal state:
    #  update_period
    #  last (last update time in secs since epoch) (max value in seen,
    #	     and only updated when feed actually contains items)
    #  seen (map sha1_of_item_url -> 1)
    def __init__(self, name, feedurl,
                 mirrorDirectory=None):
        self.name=name
        self.feed=feedurl
        self.mirrorDirectory=mirrorDirectory

        self.update_period=None
        self.seen={}

        self.last=0
        self.channel=None
        self.load_state()

    def get_state(self):
        if self.update_period==None:
            # get_state called before first refresh, e.g. due to
            # network trouble while trying to refresh
            return None
        return self.feed+'\n'\
               +str(self.update_period)+'\n'\
               +str(int(self.last))+'\n'\
               +string.join(self.seen.keys(), '\n')

    def set_state(self, state):
        l=string.split(state, '\n')
        if l[0]!=self.feed:
            raise TouRSStFeedURLChangedException, (l, self.feed)
        self.update_period=int(l[1])
        self.last=int(l[2])
        self.seen={}
        for line in l[3:]:
            if line!='':
                self.seen[line]=1

    def hash(self):
        return sha.new(self.feed).hexdigest()

    def _name_tmp(self):
        return self._name()+".%s_%u.tmp"%(socket.gethostname(), os.getpid())

    def _name(self):
        return os.path.expanduser("~/.toursst/feedstate/%s"%(self.hash()))

    def save_state(self):
        state = self.get_state()
        if state is None:
            return
        file=None
        try:
            file=open(self._name_tmp(), 'w')
        except IOError, (err, errstr):
            if err!=errno.ENOENT:
                raise
           
            mkdir_if_missing(os.path.expanduser("~/.toursst"))
            mkdir_if_missing(os.path.expanduser("~/.toursst/feedstate"))
            file=open(self._name_tmp(), 'w')
        file.write(state)
        file.close()
        os.rename(file.name, self._name())

    def load_state(self):
        try:
            file=open(self._name())
        except IOError, (err, errstr):
            if err==errno.ENOENT:
                return
            else:
                raise
        self.set_state(file.read())
        file.close()

    def age(self):
        return time.time()-self.last

    def need_refresh(self):
        if not self.update_period:
            return True
        else:
            age=self.age()
            log.chatty("age=%r, update_period=%r"%(age, self.update_period))
            return age > self.update_period

    def refresh(self, writerlist):
        log.verbose('Refreshing...')
        starttime=time.time()

        if self.mirrorDirectory is not None:
            def _slurp(url):
                import urllib
                host, port, path = client._parse(url)
                assert path.startswith('/'), 'URL path should start with a slash'
                path = path[1:]
                path = urllib.quote_plus(path, '?=/')
                if port != 80:
                    host = '%s:%d' % (host, port)
                f = file(os.path.expanduser(os.path.join(self.mirrorDirectory, host, path)))
                data = f.read()
                return data
            d = defer.succeed(self.feed)
            d.addCallback(_slurp)

            # fall back to network use if local fail is broken or missing
            d.addErrback(lambda _, url: client.getPage(url), self.feed)
        else:
            d = client.getPage(self.feed)
        d.addCallback(microdom.parseString, beExtremelyLenient=1)
        d.addCallback(RSSParser, starttime)
        d.addCallback(self._cbRefresh, writerlist, starttime)
        """
        try:
            dom = makeBlocking(d)
        except (error.ConnectError, error.ConnectionLost), e:
            log.verbose('Connection broke: %s' % e)
            return
        except ValueError, (httpErrorCode, errorString):
            log.verbose('HTTP error %s: %s' % (httpErrorCode, errorString))
            return
        rss = RSSParser(dom, starttime)
        """
        return d

    def _cbRefresh(self, rss, writerlist, starttime):
        self.title=rss.getTitle()

        self.update_period=rss.get_update_period()

        old_seen=self.seen
        self.seen={}
        saw_old_ones=0
        for item in rss.getItems():
            if not old_seen.has_key(item.hash()):
                log.chatty('New item.')
                for writer in writerlist:
                    writer.store(item)
            else:
                saw_old_ones=1
            self.ack(item, starttime)
        if not saw_old_ones and old_seen!={}:
            log.critical("No overlap since last update, you may have missed some items")
        self.save_state()

    def ack(self, item, time):
        self.seen[item.hash()]=1
        self.last=time

    def __repr__(self):
        return '<%s url=%s update_period=%s last=%d seen=%s>'\
               %(self.__class__.__name__, self.feed,
                 str(self.update_period), self.last, str(self.seen))
