import sys
import os.path

from twisted.python import usage
from twisted.internet import reactor, defer

from TouRSSt import fetch, log, xbel

class TouRSStOptions(usage.Options):
    """A modular RSS fetcher"""

    optFlags = [
        ('force-refresh', None, 'Force refresh on all feeds'),
        ('list-writers', None, 'List plugins to write the RSS items'),
        ]

    optParameters = [
        ('bookmark-file', None,
         os.path.expanduser('~/.galeon/bookmarks.xbel'),
         'Location of XBEL bookmarks'),
         
        ('bookmark-folder', None,
         'RSS',
         'Bookmark folder RSS bookmarks are in (empty string for top folder)'),

        ('mirror', None,
         None,
         'Directory that stores pre-mirrored RSS feeds.'),
        ]

    defaultSubCommand = 'maildir'

    def __init__(self):
        usage.Options.__init__(self)
        self['verbosity'] = 0 # default

        self.subCommands = []
        for kludge in ['stdout', 'maildir']:
            module = __import__('TouRSSt.writer.{0}'.format(kludge), fromlist=[''])
            options = getattr(module, 'Options')
            self.subCommands.append((
                kludge, None, options, module.__doc__))

    def opt_verbose(self):
        """Be more verbose"""
        self['verbosity'] = self['verbosity']+1

    opt_v = opt_verbose

    def opt_quiet(self):
        """Be less verbose"""
        self['verbosity'] = self['verbosity']-1

    opt_q = opt_quiet

class TouRSStApp:
    """A modular RSS fetcher"""
    def __init__(self):
        self.config = TouRSStOptions()
        try:
            self.config.parseOptions()
        except usage.UsageError, errortext:
            print >>sys.stderr, '%s: %s' % (sys.argv[0], errortext)
            print >>sys.stderr, '%s: Try --help for usage details.' % (sys.argv[0])
            sys.exit(1)

    def _reportError(self, fail, feed):
        print >>sys.stderr, '%s: error while fetching %s: %s.' % (
            sys.argv[0],
            feed.feed,
            fail.getErrorMessage(),
            )

    def run(self):
        try:
            log.setLevel(self.config['verbosity'])

            writer = self.config.subOptions.getTouRSStWriter()
            deferreds = []
            for name, url in xbel.getRSSFeedsFromXBEL(
                filename=self.config['bookmark-file'],
                folderName=self.config['bookmark-folder'],
                ):
                log.verbose('Checking feed', name)
                feed=fetch.TouRSStFeed(name, url,
                                       mirrorDirectory=self.config['mirror'])
                feedWriter = writer.startWriting(feed)
                if feed.need_refresh() or self.config['force-refresh']:
                    d = feed.refresh([feedWriter])
                else:
                    d = defer.succeed(None)
                d.addCallback(lambda _, feedWriter: feedWriter.stopWriting(), feedWriter)
                deferreds.append((feed, d))
            dl = defer.DeferredList([d for feed, d in deferreds])
            for feed, d in deferreds:
                d.addErrback(self._reportError, feed)
            dl.addBoth(lambda _, writer: writer.stopWriting(), writer)
            dl.addBoth(lambda _: reactor.callWhenRunning(reactor.stop))
            reactor.run()
        except KeyboardInterrupt:
            print >>sys.stderr, '%s: interrupted.' % sys.argv[0]
            sys.exit(1)
