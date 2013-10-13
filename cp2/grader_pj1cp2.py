#!/usr/bin/env python

import sys
import os
import socket
import random
import time
import StringIO
import hashlib
from subprocess import check_call
import requests
import resource
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

sys.path.append('../common/')


import datetime
from grader_super import Project1Grader, Project1Test
from plcommon import check_output, check_both

USAGE =\
    '%s <andrewid> -- this will begin the interactive grader for PJ1CP2'

DUE_DATE = datetime.datetime(2013, 9, 24, 23, 59, 59)
SOURCE_REMINDER = '''\n\n(1) Ensure usage of select()\n
(2) Check documentation\n
(3) Check readability/modularity'''


class Checkpoint2Test(Project1Test):

    def test_apache_bench(self):
        print '----- Testing Apache Bench -----'
        check_output('echo "----- Testing Apache Bench ----" >> %s' % self.grader.results)
        check_output('echo "ab -kc 800 -n 100000 http://127.0.0.1:%d/index.html" >> %s' % (self.port, self.grader.results))
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        cmd = 'ab -kc 800 -n 100000 http://127.0.0.1:%d/index.html >> %s' % (self.port, self.grader.results)
        self.pAssertEqual(0, os.system(cmd))

class Checkpoint2Grader(Project1Grader):
    def __init__(self, andrewid):
        super(Checkpoint2Grader,self).__init__(andrewid, 2, DUE_DATE, SOURCE_REMINDER)
        self.editor = 'vim'
    
    def prepareTestSuite(self):
        super(Checkpoint2Grader, self).prepareTestSuite()
        self.suite.addTest(Checkpoint2Test('test_HEAD_headers', self))
        self.suite.addTest(Checkpoint2Test('test_HEAD', self))
        self.suite.addTest(Checkpoint2Test('test_GET', self))
        self.suite.addTest(Checkpoint2Test('test_POST', self))
        self.suite.addTest(Checkpoint2Test('test_bw', self))
        self.suite.addTest(Checkpoint2Test('test_apache_bench', self))

        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE % sys.argv[0]
        exit(1)

    grader = Checkpoint2Grader(sys.argv[1])
    grader.prepareTestSuite()
    grader.runTests()
