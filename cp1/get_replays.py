#!/usr/bin/env python

import sys
sys.path.append('../common/')

from plcommon import check_both


andrewids = open('../common/andrewids').read().split('\n')[:-1]
for a in andrewids:
    print a
    check_both("./get_replays.sh %s" % a)

