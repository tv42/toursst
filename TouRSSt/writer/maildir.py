import time
import os
import os.path
import string

from TouRSSt.writer import base
from TouRSSt import safefilenames, log

from twisted.python import plugin
from twisted.mail import maildir

starttime=int(time.time())

count=0
def getcount():
    global count
    count=count+1
    return count

def mailfolder_join(*folders):
    folders=filter(lambda f: f!=None, folders)
    if folders==[]:
        return None
    else:
        return string.join(folders, '.')

class TouRSStWriterMaildir(base.TouRSStWriterBase):
    """Write an RSS item into a maildir"""

    def __init__(self, config):
        base.TouRSStWriterBase.__init__(self, config)
        self.formatter = None
        for plug in plugin.getPlugIns('TouRSSt.format.email'):
            if plug.name == self.config['maildir-formatter']:
                module = plug.load()
                klass = getattr(module, 'toursstFormatter')
                self.formatter = klass()
                break
        if self.formatter is None:
            raise 'unable to load email formatter: %r' % (self.config['maildir-formatter'])
        self.foldersSeen = {}

    def startWriting(self, feed):
        class _Writer:
            def __init__(self, config, formatter, feed):
                self.formatter=formatter
                self.feed=feed

                folder=config['folder']
                if config['feeds-in-folders']:
                    folder=mailfolder_join(
                        folder,
                        safefilenames.makesafe(
                        string.strip(self.feed.name)))
                    log.chatty('Storing to Maildir', config['maildir'],
                               folder
                               and 'folder '+folder
                               or 'default folder')
                dir = config['maildir']
                if folder is not None:
                    dir = os.path.join(dir, '.'+folder)
                self.dir = dir

            def store(self, item):
                maildir.initializeMaildir(self.dir)
                fname = maildir._generateMaildirName()
                filename = os.path.join(self.dir, 'tmp', fname)
                fp = open(filename, 'w')
                msg = maildir.MaildirMessage(
                    'toursst@invalid',
                    fp,
                    filename,
                    os.path.join(self.dir, 'new', fname))
                data = self.formatter.format(item, self.feed)
                for line in data.splitlines():
                    msg.lineReceived(line)
                msg.eomReceived()

            def stopWriting(self):
                pass

        feedWriter = _Writer(self.config, self.formatter, feed)
        self.foldersSeen[feedWriter.dir]=1
        return feedWriter

    def _sawFolders(self, seen):
        for k,v in seen.items():
            if k not in self.foldersSeen:
                self.foldersSeen[k]=[]
            self.foldersSeen[k].extend(v)

    def stopWriting(self):
        filename = os.path.join(self.config['maildir'], 'toursst-mailboxes.muttrc')
        f = open(filename + '.tmp', 'w')
        f.write('mailboxes ')
        f.write(' '.join(['"%s"' % dir for dir in self.foldersSeen.keys()]))
        f.write('\n')
        f.close()
        os.rename(filename+'.tmp', filename)

class Options(base.Options):
    """Write an RSS item into a maildir"""

    writer = TouRSStWriterMaildir

    def __init__(self):
        base.Options.__init__(self)
        self['feeds-in-folders'] = True # default

    def opt_feeds_in_folders(self):
        """Write feeds into subfolders"""
        self['feeds-in-folders'] = True

    def opt_no_feeds_in_folders(self):
        """Do not write feeds into subfolders"""
        self['feeds-in-folders'] = False

    optParameters = [
        ('maildir', None, os.path.expanduser('~/Maildir'),
         'Maildir to use'),
        ('folder', None, 'TouRSSt',
         'Folder to use'),
        ('maildir-formatter', None, 'simple',
         'Style of email stored'),
        ]
