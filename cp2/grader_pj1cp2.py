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

MIME = {
            '.html' : 'text/html',
            '.css'  : 'text/css',
            '.png'  : 'image/png',
            '.jpg'  : 'image/jpeg',
            '.gif'  : 'image/gif',
            ''      : 'application/octet-stream'
       }

class Checkpoint2Test(Project1Test):
    def equal_files(self, fname1, fname2):
        outhash = 0
        out2hash = 1
        with open(fname1) as f:
            with open(fname2) as f2:
                outhash = hashlib.sha256(f.read()).hexdigest()
                out2hash = hashlib.sha256(f2.read()).hexdigest()
        self.pAssertEqual(outhash, out2hash)
    
    def check_headers(self, response_type, headers, length_content, ext):
        self.pAssertEqual(headers['Server'].lower(), 'liso/1.0')

        try:
            datetime.datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z')
        except KeyError:
            self.print_str('Bad Date header')
        except:
            self.print_str('Bad Date header: %s' % (headers['Date']))
        
        self.pAssertEqual(int(headers['Content-Length']), length_content)
        #self.pAssertEqual(headers['Connection'].lower(), 'close')

        if response_type == 'GET' or response_type == 'HEAD':
            header_set = set(['connection', 'content-length',
                              'date', 'last-modified',
                              'server', 'content-type'])
            self.pAssertEqual(set(), header_set - set(headers.keys()))
            if headers['Content-Type'].lower() != MIME[ext]:
                self.print_str('MIME got %s expected %s' % (headers['Content-Type'].lower(), MIME[ext]))
            self.pAssertTrue(headers['Content-Type'].lower() == MIME[ext] or
                            headers['Content-Type'].lower() == MIME['.html'])

            try:
                datetime.datetime.strptime(headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S %Z')
            except:
                self.print_str('Bad Last-Modified header: %s' % (headers['Last-Modified']))
        elif response_type == 'POST':
            header_set = set(['connection', 'content-length',
                              'date', 'server'])
            self.pAssertEqual(set(), header_set - set(headers.keys()))
        else:
            self.fail('Unsupported Response Type...')
    
    def test_HEAD_headers(self):
        self.print_str('----- Testing Headers -----')
        tests = {
            'http://127.0.0.1:%d/index.html' : 
            ('f5cacdcb48b7d85ff48da4653f8bf8a7c94fb8fb43407a8e82322302ab13becd', 802),
            'http://127.0.0.1:%d/images/liso_header.png' :
            ('abf1a740b8951ae46212eb0b61a20c403c92b45ed447fe1143264c637c2e0786', 17431),
            'http://127.0.0.1:%d/style.css' :
            ('575150c0258a3016223dd99bd46e203a820eef4f6f5486f7789eb7076e46736a', 301)
                }
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.head(test % self.port, timeout=10.0)
            self.check_headers(response.request.method,
                               response.headers,
                               tests[test][1],
                               ext)

    def test_HEAD(self):
        self.print_str('----- Testing HEAD -----')
        tests = {
            'http://127.0.0.1:%d/index.html' : 
            ('f5cacdcb48b7d85ff48da4653f8bf8a7c94fb8fb43407a8e82322302ab13becd', 802),
            'http://127.0.0.1:%d/images/liso_header.png' :
            ('abf1a740b8951ae46212eb0b61a20c403c92b45ed447fe1143264c637c2e0786', 17431),
            'http://127.0.0.1:%d/style.css' :
            ('575150c0258a3016223dd99bd46e203a820eef4f6f5486f7789eb7076e46736a', 301)
                }
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.head(test % self.port, timeout=10.0)
            contenthash = hashlib.sha256(response.content).hexdigest()
            self.pAssertEqual(200, response.status_code)
            #self.check_headers(response.request.method,
            #                   response.headers,
            #                   tests[test][1],
            #                   ext)

    def test_GET(self):
        self.print_str('----- Testing GET -----')
        tests = {
            'http://127.0.0.1:%d/index.html' : 
            'f5cacdcb48b7d85ff48da4653f8bf8a7c94fb8fb43407a8e82322302ab13becd',
            'http://127.0.0.1:%d/images/liso_header.png' :
            'abf1a740b8951ae46212eb0b61a20c403c92b45ed447fe1143264c637c2e0786',
            'http://127.0.0.1:%d/style.css' :
            '575150c0258a3016223dd99bd46e203a820eef4f6f5486f7789eb7076e46736a'
                }
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        for test in tests:
            root,ext = os.path.splitext(test)
            response = requests.get(test % self.port, timeout=10.0)
            contenthash = hashlib.sha256(response.content).hexdigest()
            self.pAssertEqual(200, response.status_code)
            self.pAssertEqual(contenthash, tests[test])
            #self.check_headers(response.request.method,
            #                   response.headers,
            #                   len(response.content),
            #                   ext)

    def test_POST(self):
        self.print_str('----- Testing POST -----')
        tests = {
            'http://127.0.0.1:%d/index.html' : 
            'f5cacdcb48b7d85ff48da4653f8bf8a7c94fb8fb43407a8e82322302ab13becd',
                }
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        for test in tests:
            root,ext = os.path.splitext(test)
            # for checkpoint 2, this should time out; we told them to swallow the data and ignore
            try:
                response = requests.post(test % self.port, data='dummy data', timeout=3.0)
            #except requests.exceptions.Timeout:
            except requests.exceptions.RequestException:
                print 'timeout'
                continue
            except socket.timeout:
                print 'socket.timeout'
                continue

            # if they do return something, make sure it's OK
            self.pAssertEqual(200, response.status_code)
            #self.check_headers(response.request.method,
            #                   response.headers,
            #                   len(response.content),
            #                   ext)
       
    def test_browser(self):
        self.print_str('----- Testing Browser -----')
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        port = self.request_port()
        check_call(['firefox', 'http://127.0.0.1:%d/index.html' % (port)])
        self.confirm()
        self.edit_notes('BROWSER TEST:')

    def test_bw(self):
        print '(----- Testing BW -----'
        check_output('echo "----- Testing BW ----" >> %s' % self.grader.results)
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        name = self.run_lisod(commit.tree)
        time.sleep(3)
        #self.pAssertEqual(0, os.system('wget http://127.0.0.1:%d/big.html -O /dev/null >> %s' % (self.port, self.grader.results)))
        self.pAssertEqual(0, os.system('curl -m 10 -o /dev/null http://127.0.0.1:%d/big.html 2>> %s' % (self.port, self.grader.results)))

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
        #with open('/tmp/replays/%s.test' % self.repo,'w') as f1:
        #    with open('/tmp/replays/%s.out' % self.repo,'w') as f2:
        #        f1.write(test.data)
        #        f2.write(out.data)
        self.confirm()
        self.edit_notes('REPLAY FILES:')


class Checkpoint2Grader(Project1Grader):
    def __init__(self, andrewid):
        super(Checkpoint2Grader,self).__init__(andrewid, 2, DUE_DATE, SOURCE_REMINDER)
        self.editor = 'vim'
    
    def prepareTestSuite(self):
        super(Checkpoint2Grader, self).prepareTestSuite()
        #self.suite.addTest(Checkpoint2Test('test_replay_files', self))
        self.suite.addTest(Checkpoint2Test('test_HEAD_headers', self))
        self.suite.addTest(Checkpoint2Test('test_HEAD', self))
        self.suite.addTest(Checkpoint2Test('test_GET', self))
        self.suite.addTest(Checkpoint2Test('test_POST', self))
        #self.suite.addTest(Checkpoint2Test('test_browser', self))
        self.suite.addTest(Checkpoint2Test('test_bw', self))
        self.suite.addTest(Checkpoint2Test('test_apache_bench', self))

        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE % sys.argv[0]
        exit(1)

    grader = Checkpoint2Grader(sys.argv[1])
    grader.prepareTestSuite()
    grader.runTests()
