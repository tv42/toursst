# -*- test-case-name: TouRSSt.tests.test_safefilenames -*-

import re, string

badChars = re.compile(r'[^a-zA-Z0-9_+-]')

#TODO dead code?
def makesafe_hierarchical(s, hier_in='/', hier_out='.'):
    r=[]
    for i in string.split(s, hier_in):
        r.append(makesafe(i))
    return string.join(r, hier_out)

def makesafe(s):
    while s and badChars.match(s):
        s=s[1:]
    while s and badChars.match(s[-1]):
        s=s[:-1]
    return badChars.sub('_', s)
