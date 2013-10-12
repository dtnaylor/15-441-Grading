#!/usr/bin/env python

import sys

sys.path.append('../common')

import datetime, hashlib, time, os
from subprocess import Popen
from grader_super import Project1Grader, Project1Test
from plcommon import check_output

USAGE =\
    '%s <andrewid> -- this will begin the interactive grader for PJ1CP3'

TMP_DIR = '/tmp/cp3/'
CP3_CHECKER = os.getcwd() + '/cp3_checker.py'
DUE_DATE = datetime.datetime(2013, 10, 8, 23, 59, 59)
SOURCE_REMINDER = '''\n\n(1) Ensure OpenSSL, fork, execve\n
(2) Check documentation\n
(3) Check readability/modularity'''

class Checkpoint3Test(Project1Test):


    def setUp(self):
        super(Checkpoint3Test, self).setUp()

        # save a copy of src for moss
        if not os.path.exists(self.grader.moss_dir):
            os.makedirs(self.grader.moss_dir)
        if not os.path.exists('%s/%s' % (self.grader.moss_dir, self.grader.andrewid)):
            print 'Saving copy of source for moss in %s/%s' % (self.grader.moss_dir, self.grader.andrewid)
            os.makedirs('%s/%s' % (self.grader.moss_dir, self.grader.andrewid))
            check_output('cp -r . %s/%s/' % (self.grader.moss_dir, self.grader.andrewid))

    def lisod_start(self):
        commit = self.resolve_tag()
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        
       
    def test_browserTLS(self):
        print '----- Testing TLS Browser -----'
        self.lisod_start()
        check_call(['firefox', 'https://127.0.0.1:%d/index.html' % (self.grader.tls_port)])
        self.confirm()
        self.edit_notes('TLS BROWSER:')


    def test_blog(self):
        print '----- Testing Blog -----'
        self.lisod_start()
        check_call(['firefox', 'http://127.0.0.1:%d/cgi/' % (self.grader.port)])
        self.confirm()
        self.edit_notes('BLOG TEST:')

    def test_cgi(self):
        print '----- Testing CGI -----'
        self.lisod_start()
        check_call(['firefox', 'http://127.0.0.1:%d/cgi/' % (self.grader.port)])
        self.confirm()
        self.edit_notes('CGI TEST:')

    def test_pipeliningTLS(self):
        print '----- Testing TLS pipelining -----'
        self.lisod_start()
        cmd = 'ncat --ssl -i 1s 127.0.0.1 %d < ./pipelining.get'
        self.assertEqual(512, os.system(cmd % (self.grader.tls_port)))

    def test_pipelining(self):
        print '----- Testing pipelining -----'
        self.lisod_start()
        cmd = 'ncat -i 1s 127.0.0.1 %d < ./pipelining.get'
        self.assertEqual(512, os.system(cmd % (self.grader.port)))

    def test_invalidPUT(self):
        print '----- Testing Bad PUT -----'
        tests = {
            'http://127.0.0.1:%d/index.html' : 
            'f5cacdcb48b7d85ff48da4653f8bf8a7c94fb8fb43407a8e82322302ab13becd',
            'http://127.0.0.1:%d/images/liso_header.png' :
            'abf1a740b8951ae46212eb0b61a20c403c92b45ed447fe1143264c637c2e0786',
            'http://127.0.0.1:%d/readme' :
            '5d4b6498d1d555b631c1c7b005144376dacb33eb99dc586b78297ade1eded9a3',
            'http://127.0.0.1:%d/style.css' :
            '575150c0258a3016223dd99bd46e203a820eef4f6f5486f7789eb7076e46736a'
                }
        self.lisod_start()
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.put(test % self.grader.port, timeout=10.0)
            self.assertEqual(501, response.status_code)

    def test_invalidLENGTH(self):
        print '----- Testing Bad Length Post -----'
        self.lisod_start()
        cmd = 'ncat -i 1s 127.0.0.1 %d < ./bad.post'
        self.assertEqual(512, os.system(cmd % (self.grader.port)))

    def test_invalidEND(self):
        print '----- Testing Bad Ending GET -----'
        self.lisod_start()
        cmd = 'ncat -i 1s 127.0.0.1 %d < ./bad.get'
        self.assertEqual(256, os.system(cmd % (self.grader.port)))


class Checkpoint3Grader(Project1Grader):
    def __init__(self, andrewid):
        super(Checkpoint3Grader, self).__init__(andrewid, 3, DUE_DATE, SOURCE_REMINDER)
        self.editor = 'emacs -nw'
        self.moss_dir = os.path.join(self.tmp_dir, 'moss')


    def prepareTestSuite(self):
        #super(Checkpoint3Grader, self).prepareTestSuite()
        #self.suite.addTest(Checkpoint3Test('test_replay_files', self))
        #self.suite.addTest(Checkpoint3Test('test_headers', self))
        #self.suite.addTest(Checkpoint3Test('test_HEAD', self))
        # self.suite.addTest(Checkpoint3Test('test_GET', self))
        # self.suite.addTest(Checkpoint3Test('test_POST', self))
        #self.suite.addTest(Checkpoint3Test('test_pipelining', self))
        #self.suite.addTest(Checkpoint3Test('test_pipeliningTLS', self))
        #self.suite.addTest(Checkpoint3Test('test_browserTLS', self))
        #self.suite.addTest(Checkpoint3Test('test_invalidPUT', self))
        #self.suite.addTest(Checkpoint3Test('test_invalidLENGTH', self))
        #self.suite.addTest(Checkpoint3Test('test_invalidEND', self))
        #self.suite.addTest(Checkpoint3Test('test_browser', self))
        #self.suite.addTest(Checkpoint3Test('test_cgi', self))
        #self.suite.addTest(Checkpoint3Test('test_blog', self))
        #self.suite.addTest(Checkpoint3Test('test_bw', self))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE % sys.argv[0]
        exit(1)

    grader = Checkpoint3Grader(sys.argv[1])
    grader.prepareTestSuite()
    grader.runTests()

