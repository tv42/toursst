import sys

_level = 0

def setLevel(level):
    global _level
    _level = level

def say(level, *a):
    if _level >= level:
        sys.stdout.write(' '.join([str(x) for x in a]) + '\n')

def chatty(*a):
    say(2, *a)

def verbose(*a):
    say(1, *a)

def critical(*a):
    say(-1, *a)
