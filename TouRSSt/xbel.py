from __future__ import generators
import os.path
import urllib
from twisted.web import microdom, domhelpers

def parseXBEL(filename=None):
    if filename is None:
        filename = os.path.expanduser('~/.galeon/bookmarks.xbel')
    bookmarks = file(filename)
    dom = microdom.parse(bookmarks)
    return dom

def findRSSFolder(dom, folderName=None):
    if folderName is None:
       folderName = 'RSS'
    if folderName == '':
        return dom
    for folder in domhelpers.findNodesNamed(dom, 'folder'):
        for title in domhelpers.findNodesNamed(folder, 'title'):
            text = domhelpers.getNodeText(title)
            if text == folderName:
                return folder
    return None

def extractRSSFeeds(dom):
    for bookmark in domhelpers.findNodesNamed(dom, 'bookmark'):
        titleNodes = domhelpers.findNodesNamed(bookmark, 'title')
        if titleNodes:
            title = domhelpers.getNodeText(titleNodes[0])
        else:
            title = None

        url = bookmark.getAttribute('href')
        url = urllib.unquote(url)
        yield title, url

def getRSSFeedsFromXBEL(filename=None, folderName=None):
    dom = parseXBEL(filename)
    folder = findRSSFolder(dom, folderName)
    if folder is None:
        return ()
    return extractRSSFeeds(folder)

if __name__ == '__main__':
    for title, url in getRSSFeedsFromXBEL():
        print '%s: %s' % (title, url)
