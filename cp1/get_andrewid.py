#!/usr/bin/env python

import sys
sys.path.append('../common/')

from plcommon import check_both

ANDREW_PATH = '/afs/andrew/course/15/441-641/'
REPO_NAME = '-15-441-project-1/.git/'
BARE_REPO_NAME = '-15-441-project-1/branches/'

out = check_both('ls -la %s' % ANDREW_PATH, False)[0][0].split('\n')[3:-1]
out = [o.split(' ')[-1] for o in out]

i = 0
j = 0
k = 0
for o in out:
    try:
        check_both('ls -la %s%s/%s%s' % (ANDREW_PATH, o, o, REPO_NAME), False)
        print o
        i += 1
    except:
        try:
            check_both('ls -la %s%s/%s%s' % (ANDREW_PATH, o, o, BARE_REPO_NAME), False)
            i += 1
        except:
            o2 = check_both('ls -la %s%s' % (ANDREW_PATH, o), False)[0][0].split('\n')[3:-1]
            if not o2:
                j += 1
            else:
                #print o
                k += 1
#print len(out)
#print i, j, k
