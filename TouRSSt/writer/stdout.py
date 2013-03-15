"""
Writes RSS items to standard output.
"""

from TouRSSt.writer import base

class TouRSStWriterStdout(base.TouRSStWriterBase):
    """Write an RSS item to standard output"""

    def __init__(self, config):
        base.TouRSStWriterBase.__init__(self, config)
        self.formatter = None
        module = __import__('TouRSSt.format.email.simple', fromlist=[''])
        klass = getattr(module, 'toursstFormatter')
        self.formatter = klass()
        if self.formatter is None:
            raise 'unable to load email formatter: %r' % 'simple'

    def startWriting(self, feed):
        class _Writer:
            def __init__(self, formatter, feed):
                self.formatter=formatter
                self.feed=feed
            def store(self, item):
                s=self.formatter.format(item, self.feed)
                s=str(s)
                print s
            def stopWriting(self):
                pass
        return _Writer(self.formatter, feed)

class Options(base.Options):
    writer = TouRSStWriterStdout
