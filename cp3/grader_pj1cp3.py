#!/usr/bin/env python

import sys

sys.path.append('../common')

import datetime, hashlib, time, os, requests
from subprocess import Popen, check_call
from grader_super import Project1Grader, Project1Test
from plcommon import check_output

USAGE =\
    '%s <andrewid> -- this will begin the interactive grader for PJ1CP3'

TMP_DIR = '/tmp/cp3/'
CP3_CHECKER = os.getcwd() + '/cp3_checker.py'
CP3_DIR = os.getcwd()
DUE_DATE = datetime.datetime(2013, 10, 8, 23, 59, 59)
SOURCE_REMINDER = '''\n\n(1) Ensure OpenSSL, fork, execve\n
(2) Check documentation\n
(3) Check readability/modularity'''
BAD_POST_DATA = 'asldksjdklfjaskldfjlksdjgjksdhfjkgdhjkfshcvkljsdclkmzxvm,xcnm,vnsdilfuodghiouwerhfguiohsdiourghiousdrhguio'
TEST_DOMAIN = 'https://dnaylor.no-ip.biz'
SIGNER_CERT = os.getcwd() + '/../common/signer.crt'
FLASKR_LOGIN_STRING = '<li><em>Unbelievable.  No entries here so far</em>'
FLASKR_USER_DATA = 'username=admin&password=default'
FLASKR_LOGGED_IN_STRING = '<div class=flash>You were logged in</div>'

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
        time.sleep(1)

    # test replay.test and replay.out up to snuff
    def test_replay_files(self):
        self.print_str('\n\n----- Testing replay.[test|out] files -----')
        commit = self.resolve_tag()
        tree = commit.tree
        print '\n----- replay.test -----'
        test = self.find_file('replay.test', tree)
        out = self.find_file('replay.out', tree)
        print test.data.replace('\n','\\n\n').replace('\r','\\r'),
        print '\n----- replay.out -----'
       	print out.data.replace('\n','\\n\n').replace('\r','\\r'),
        self.confirm()
        self.edit_notes('REPLAY FILES:')
        
    def test_pipelining(self):
        print '----- Testing pipelining -----'
        self.lisod_start()
        cmd = 'ncat -i 1s 127.0.0.1 %d > /dev/null < ' + CP3_DIR + '/pipelining-keepalive.get'
        self.pAssertEqual(256, os.system(cmd % (self.port)))
        cmd = 'ncat -i 1s 127.0.0.1 %d > /dev/null < ' + CP3_DIR + '/pipelining-close.get'
        self.pAssertEqual(0, os.system(cmd % (self.port)))

    def test_pipeliningTLS(self):
        print '----- Testing TLS pipelining -----'
        self.lisod_start()
        cmd = 'ncat --ssl -i 1s 127.0.0.1 %d > /dev/null < ' + CP3_DIR + '/pipelining-keepalive.get'
        self.pAssertEqual(256, os.system(cmd % (self.tls_port)))
        cmd = 'ncat --ssl -i 1s 127.0.0.1 %d > /dev/null < ' + CP3_DIR + '/pipelining-close.get'
        self.pAssertEqual(0, os.system(cmd % (self.tls_port)))

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
            response = requests.put(test % self.port, timeout=10.0)
            self.pAssertEqual(501, response.status_code)

    def test_invalidLENGTH(self):
        print '----- Testing Bad Length Post -----'
        self.lisod_start()
        s = requests.Session()
        prepped = requests.Request('POST', 'http://127.0.0.1:%d/cgi/' % self.port, data=BAD_POST_DATA, headers={'Connection':'Close'}).prepare()
        prepped.headers['Content-Length'] = -1000
        response = s.send(prepped, timeout=10.0)
        print response.status_code
        reasonable_codes = [400, 411, 413]
        self.pAssertEqual(True, response.status_code in reasonable_codes)

    def test_invalidEND(self):
        print '----- Testing Bad Ending GET -----'
        self.lisod_start()
        s = requests.Session()
        prepped = requests.Request('GET', 'http://127.0.0.1:%d/index.html' % self.port, data=BAD_POST_DATA, headers={'Conn\r\n\r\nection':'Cl\r\nwose'}).prepare()
        response = s.send(prepped, timeout=1.0)
        print response.status_code
        # print response.text
        self.pAssertEqual(400, response.status_code)

    def test_browser(self):
        self.print_str('----- Testing Browser -----')
        self.lisod_start()
        response = requests.get('http://127.0.0.1:%d/index.html' % (self.port), timeout=1.0)
        self.pAssertEqual(200, response.status_code)

    def test_browserTLS(self):
        print '----- Testing TLS Browser -----'
        self.lisod_start()
        response = requests.get('%s:%d/index.html' % (TEST_DOMAIN, self.tls_port), verify=SIGNER_CERT, timeout=1.0)
        self.pAssertEqual(200, response.status_code)

    def test_cgi(self):
        print '----- Testing CGI -----'
        self.lisod_start()
        response = requests.get('http://127.0.0.1:%d/cgi/' % (self.port), timeout=1.0)
        self.pAssertEqual(200, response.status_code)
        rm = [l for l in response.text.split('\n') if 'REQUEST_METHOD' in l][0]
        method = rm.split('<DD>')[1].strip()
        self.pAssertEqual('GET', method)
       
    def test_blog(self):
        print '----- Testing Blog -----'
        self.change_cgi(self.grader.tmp_dir + 'cgi/wsgi_wrapper.py')
        self.lisod_start()
        response = requests.get('http://127.0.0.1:%d/cgi/' % (self.port), timeout=3.0)
        self.pAssertEqual(200, response.status_code)
        login = [l for l in response.text.split('\n') if 'No entries' in l][0].strip()
        self.pAssertEqual(FLASKR_LOGIN_STRING, login)

        s = requests.Session()
        prepped = requests.Request('POST', 'http://127.0.0.1:%d/cgi/login' % self.port, data=FLASKR_USER_DATA, headers={'Content-Type':'application/x-www-form-urlencoded'}).prepare()
        response = s.send(prepped, timeout = 3.0)
        self.pAssertEqual(200, response.status_code)
        login = [l for l in response.text.split('\n') if 'were logged in' in l][0].strip()
        self.pAssertEqual(FLASKR_LOGGED_IN_STRING, login)


class Checkpoint3Grader(Project1Grader):
    def __init__(self, andrewid):
        super(Checkpoint3Grader, self).__init__(andrewid, 3, DUE_DATE, SOURCE_REMINDER)
        self.editor = 'emacs -nw'
        self.moss_dir = os.path.join(self.tmp_dir, 'moss')


    def prepareTestSuite(self):
        super(Checkpoint3Grader, self).prepareTestSuite()
        # Shared with CP2
        self.suite.addTest(Checkpoint3Test('test_HEAD_headers', self))
        self.suite.addTest(Checkpoint3Test('test_HEAD', self))
        self.suite.addTest(Checkpoint3Test('test_GET', self))
        self.suite.addTest(Checkpoint3Test('test_POST', self))
        self.suite.addTest(Checkpoint3Test('test_bw', self))
        
        # CP3 specific
        self.suite.addTest(Checkpoint3Test('test_replay_files', self))
        self.suite.addTest(Checkpoint3Test('test_pipelining', self))
        self.suite.addTest(Checkpoint3Test('test_pipeliningTLS', self))
        self.suite.addTest(Checkpoint3Test('test_invalidPUT', self))
        self.suite.addTest(Checkpoint3Test('test_invalidLENGTH', self))
        self.suite.addTest(Checkpoint3Test('test_invalidEND', self))
        self.suite.addTest(Checkpoint3Test('test_browser', self))
        self.suite.addTest(Checkpoint3Test('test_browserTLS', self))
        self.suite.addTest(Checkpoint3Test('test_cgi', self))
        self.suite.addTest(Checkpoint3Test('test_blog', self))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE % sys.argv[0]
        exit(1)

    grader = Checkpoint3Grader(sys.argv[1])
    grader.prepareTestSuite()
    grader.runTests()

