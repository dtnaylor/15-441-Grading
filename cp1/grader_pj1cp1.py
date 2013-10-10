#!/usr/bin/env python

import sys

sys.path.append('../common/')


import datetime, hashlib, time, os
from subprocess import Popen
from grader_super import Project1Grader, Project1Test
from plcommon import check_output

USAGE =\
    '%s <andrewid> -- this will begin the interactive grader for PJ1CP1'

TMP_DIR = '/tmp/cp1/'
CP1_CHECKER = os.getcwd() + '/cp1_checker.py'
DUE_DATE = datetime.datetime(2013, 9, 10, 23, 59, 59)
SOURCE_REMINDER = '''\n\n(1) Ensure usage of select()\n
(2) Check documentation\n
(3) Check readability/modularity'''

class Checkpoint1Test(Project1Test):
    # test replay.test and replay.out up to snuff
    def test_replay_files(self):
        self.print_str('\n\n----- Testing replay.[test|out] files -----')
        commit = self.resolve_tag()
        tree = commit.tree
        self.print_str('\n----- replay.test -----')
        test = self.find_file('replay.test', tree)
        out = self.find_file('replay.out', tree)
        testhash = hashlib.sha256(test.data).hexdigest()
        outhash = hashlib.sha256(out.data).hexdigest()
        self.print_str('\treplay.test: %s' % testhash)
        self.print_str('\treplay.out : %s' % outhash)
        self.pAssertEqual(testhash, outhash)

    # test with our test python script
    def test_cp1_checker(self):
        self.print_str('\n\n----- Testing cp1_checker -----')
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        # 100 trials, 50 random r+w pairs inside, .05% chance disconnect after
        # each r and each w, 32768 bytes sent (32KB), 800 connections
        command = '%s localhost %d 100 50 32768 800' % (CP1_CHECKER, self.port)
        print 'running %s' % command.split(' ')
        process = Popen(command.split(' '))
 
        for i in xrange(60): # try at most for 60 seconds
            time.sleep(1)
            if process.poll() != None: 
                rc = process.returncode
                if rc != 0:
                    raise Exception("Command '%s' returned non-zero exit status %s" % (command, rc))
                return
        process.kill()
        raise Exception("Timeout")


class Checkpoint1Grader(Project1Grader):
    def __init__(self, andrewid):
        super(Checkpoint1Grader,self).__init__(andrewid, 1, DUE_DATE, SOURCE_REMINDER)
        self.editor = 'emacs -nw'
    
    def prepareTestSuite(self):
        super(Checkpoint1Grader, self).prepareTestSuite()
        self.suite.addTest(Checkpoint1Test('test_replay_files', self))
        self.suite.addTest(Checkpoint1Test('test_cp1_checker', self))

        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE % sys.argv[0]
        exit(1)

    grader = Checkpoint1Grader(sys.argv[1])
    grader.prepareTestSuite()
    grader.runTests()
