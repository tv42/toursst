from twisted.trial import unittest
from TouRSSt import safefilenames

class TestSafeFileNames(unittest.TestCase):
    def test_valid(self):
        self.failUnlessEqual(safefilenames.makesafe('abc0+42-99XYZ'), 'abc0+42-99XYZ')

    def test_empty(self):
        self.failUnlessEqual(safefilenames.makesafe(''), '')

    def test_knownBad(self):
        self.failUnlessEqual(safefilenames.makesafe(' ./,\\\n\r!\0'), '')

    def test_knownBadWithUnderscoresHidden(self):
        self.failUnlessEqual(safefilenames.makesafe(' ./,\\_\n_\r!\0'), '___')

    def test_intermixed(self):
        self.failUnlessEqual(safefilenames.makesafe('foo/Bar.baz'), 'foo_Bar_baz')

    def test_leadingBadCharsRemoved(self):
        self.failUnlessEqual(safefilenames.makesafe('!!!foo'), 'foo')

    def test_trailingBadCharsRemoved(self):
        self.failUnlessEqual(safefilenames.makesafe('foo!!!'), 'foo')

    def test_leadingUnderscoresNotRemoved(self):
        self.failUnlessEqual(safefilenames.makesafe('___foo'), '___foo')

    def test_trailingUnderscoresNotRemoved(self):
        self.failUnlessEqual(safefilenames.makesafe('foo___'), 'foo___')

    def test_attacks(self):
        self.failUnlessEqual(safefilenames.makesafe('../../etc/passwd'), 'etc_passwd')

