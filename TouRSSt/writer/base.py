from twisted.python import usage

class TouRSStWriterBase:
    """Base class for writing out an RSS item."""

    def __init__(self, config):
        self.config = config

    def startWriting(self, feed):
        """Return an object with methods store(item) and stopWriting()"""
        raise NotImplementedError

    def stopWriting(self):
        pass

class Options(usage.Options):
    writer = None

    def getTouRSStWriter(self):
        assert self.writer is not None, \
               'Subclasses of TouRSStWriterBase should override self.writer'
        return self.writer(self)
