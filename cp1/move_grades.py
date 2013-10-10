#!/usr/bin/env python

import sys
import os
sys.path.append('../common/')

from plcommon import check_both

CP_NUM = 1
NOTES_DIR = './results'
RESULTS_DIR = './results'
GRADES_DIR = './grades'

andrewids = open('../common/andrewids').read().split('\n')[:-1]
for a in andrewids:
    print a
    check_both("./move_grades.sh %s %d %s %s %s" % (a, CP_NUM, NOTES_DIR, RESULTS_DIR, GRADES_DIR))
