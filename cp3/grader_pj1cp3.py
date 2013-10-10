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

MIME = {
            '.html' : 'text/html',
            '.css'  : 'text/css',
            '.png'  : 'image/png',
            '.jpg'  : 'image/jpeg',
            '.gif'  : 'image/gif',
            ''      : 'application/octet-stream'
       }

class Checkpoint3Test(Project1Test):

    # test replay.test and replay.out up to snuff
    def test_replay_files(self):
        print '\n\n----- Testing replay.[test|out] files -----'
        commit = self.resolve_tag()
        tree = commit.tree
        print '\n----- replay.test -----'
        test = self.find_file('replay.test', tree)
        out = self.find_file('replay.out', tree)
        print test.data.replace('\n','\\n\n').replace('\r','\\r'),
        print '\n----- replay.out -----'
       	print out.data.replace('\n','\\n\n').replace('\r','\\r'),
        # with open('/tmp/replays/%s.test' % repo,'w') as f1:
        #     with open('/tmp/replays/%s.out' % repo,'w') as f2:
        #         f1.write(test.data)
        #         f2.write(out.data)

    def check_headers(self, response_type, headers, length_content, ext):
        self.assertEqual(headers['Server'].lower(), 'liso/1.0')

        try:
            datetime.datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
        except:
            print >> sys.stderr, 'Bad Date header: %s' % (headers['Date'])
        
        self.assertEqual(int(headers['Content-Length']), length_content)
        self.assertEqual(headers['Connection'].lower(), 'close')

        if response_type == 'GET' or response_type == 'HEAD':
            header_set = set(['connection', 'content-length',
                              'date', 'last-modified',
                              'server', 'content-type'])
            self.assertEqual(set(), header_set - set(headers.keys()))
            if headers['Content-Type'].lower() != MIME[ext]:
                print 'MIME got %s expected %s' % (headers['Content-Type'].lower(), MIME[ext])
            self.assertTrue(headers['Content-Type'].lower() == MIME[ext] or
                            headers['Content-Type'].lower() == MIME['.html'])

            try:
                datetime.datetime.strptime(headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z')
            except:
                print >> sys.stderr, 'Bad Last-Modified header: %s' % (headers['Last-Modified'])
        elif response_type == 'POST':
            header_set = set(['connection', 'content-length',
                              'date', 'server'])
            self.assertEqual(set(), header_set - set(headers.keys()))
        else:
            self.fail('Unsupported Response Type...')

    def test_HEAD(self):
        print '----- Testing HEAD -----'
        tests = {
            'http://127.0.0.1:%d/index.html' : 
            ('f5cacdcb48b7d85ff48da4653f8bf8a7c94fb8fb43407a8e82322302ab13becd', 802),
            'http://127.0.0.1:%d/images/liso_header.png' :
            ('abf1a740b8951ae46212eb0b61a20c403c92b45ed447fe1143264c637c2e0786', 17431),
            'http://127.0.0.1:%d/readme' :
            ('5d4b6498d1d555b631c1c7b005144376dacb33eb99dc586b78297ade1eded9a3', 5154304),
            'http://127.0.0.1:%d/style.css' :
            ('575150c0258a3016223dd99bd46e203a820eef4f6f5486f7789eb7076e46736a', 301)
                }
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.head(test % port, timeout=10.0)
            contenthash = hashlib.sha256(response.content).hexdigest()
            self.assertEqual(200, response.status_code)
            self.check_headers(response.request.method,
                               response.headers,
                               tests[test][1],
                               ext)
        self.confirm()
        self.edit_notes()

    def test_GET(self):
        print '----- Testing GET -----'
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
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.get(test % port, timeout=10.0)
            contenthash = hashlib.sha256(response.content).hexdigest()
            self.assertEqual(200, response.status_code)
            self.assertEqual(contenthash, tests[test])
            self.check_headers(response.request.method,
                               response.headers,
                               len(response.content),
                               ext)
        self.confirm()
        self.edit_notes()

    def test_POST(self):
        print '----- Testing POST -----'
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
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.post(test % port, timeout=10.0)
            self.assertEqual(200, response.status_code)
            self.check_headers(response.request.method,
                               response.headers,
                               len(response.content),
                               ext)
        self.confirm()
        self.edit_notes()
       
    def test_browserTLS(self):
        print '----- Testing TLS Browser -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_tlsport()
        check_call(['google-chrome', 'https://127.0.0.1:%d/index.html' % (port)])
        self.confirm()
        self.edit_notes()


    def test_browser(self):
        print '----- Testing Browser -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        check_call(['google-chrome', 'http://127.0.0.1:%d/index.html' % (port)])
        self.confirm()
        self.edit_notes()

    def test_blog(self):
        print '----- Testing Blog -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        check_call(['google-chrome', 'http://127.0.0.1:%d/cgi/' % (port)])
        self.confirm()
        self.edit_notes()

    def test_cgi(self):
        print '----- Testing CGI -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod_cgitest(commit.tree)
        time.sleep(3)
        port = self.request_port()
        check_call(['google-chrome', 'http://127.0.0.1:%d/cgi/' % (port)])
        self.confirm()
        self.edit_notes()

    def test_bw(self):
        print '----- Testing BW -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        self.assertEqual(0, os.system('wget http://127.0.0.1:%d/bw.test -O /dev/null >> /tmp/%s_notes.txt' % (port, repo)))

    def test_pipeliningTLS(self):
        print '----- Testing TLS pipelining -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_tlsport()
        cmd = 'ncat --ssl -i 1s 127.0.0.1 %d < /home/wolf/Dropbox/CMU/TA/15-441/Grading/project1/cp3/pipelining.get'
        self.confirm()
        self.assertEqual(512, os.system(cmd % (port)))

    def test_pipelining(self):
        print '----- Testing pipelining -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        cmd = 'ncat -i 1s 127.0.0.1 %d < /home/wolf/Dropbox/CMU/TA/15-441/Grading/project1/cp3/pipelining.get'
        self.confirm()
        self.assertEqual(512, os.system(cmd % (port)))
        self.edit_notes()

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
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.put(test % port, timeout=10.0)
            self.assertEqual(501, response.status_code)
        self.confirm()
        self.edit_notes()

    def test_invalidLENGTH(self):
        print '----- Testing Bad Length Post -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        cmd = 'ncat -i 1s 127.0.0.1 %d < /home/wolf/Dropbox/CMU/TA/15-441/Grading/project1/cp3/bad.post'
        self.assertEqual(512, os.system(cmd % (port)))

    def test_invalidEND(self):
        print '----- Testing Bad Ending GET -----'
        global repo
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        cmd = 'ncat -i 1s 127.0.0.1 %d < /home/wolf/Dropbox/CMU/TA/15-441/Grading/project1/cp3/bad.get'
        self.assertEqual(256, os.system(cmd % (port)))


class Checkpoint3Grader(Project1Grader):
    def __init__(self, andrewid):
        super(Checkpoint3Grader, self).__init__(andrewid, 3, DUE_DATE, SOURCE_REMINDER)
        self.editor = 'emacs -nw'


    def prepareTestSuit(self):
        super(Checkpoint3Grader, self).prepareTestSuit()
        self.suite.addTest(GradeCheckpoint3('test_replay_files'))
        self.suite.addTest(GradeCheckpoint3('test_HEAD'))
        self.suite.addTest(GradeCheckpoint3('test_GET'))
        self.suite.addTest(GradeCheckpoint3('test_POST'))
        self.suite.addTest(GradeCheckpoint3('test_pipelining'))
        self.suite.addTest(GradeCheckpoint3('test_pipeliningTLS'))
        self.suite.addTest(GradeCheckpoint3('test_browserTLS'))
        self.suite.addTest(GradeCheckpoint3('test_invalidPUT'))
        self.suite.addTest(GradeCheckpoint3('test_invalidLENGTH'))
        self.suite.addTest(GradeCheckpoint3('test_invalidEND'))
        self.suite.addTest(GradeCheckpoint3('test_browser'))
        self.suite.addTest(GradeCheckpoint3('test_cgi'))
        self.suite.addTest(GradeCheckpoint3('test_blog'))
        self.suite.addTest(GradeCheckpoint3('test_bw'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE % sys.argv[0]
        exit(1)

    grader = Checkpoint3Grader(sys.argv[1])
    grader.prepareTestSuite()
    grader.runTests()

