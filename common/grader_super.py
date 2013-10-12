#!/usr/bin/env python

import os
import datetime
import traceback
import shutil
import sys
import time
import hashlib
import random
from subprocess import Popen, check_call
from plcommon import check_output, check_both

import unittest
from pygit2 import Blob, Tree, Repository, Tag

import resource
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

ROOT_REPO_TEMPLATE = '/afs/andrew/course/15/441-641/%s/%s-15-441-project-1'
REPO_TEMPLATE = '%s-15-441-project-1'

# paths to *original* resources; will be copied to tmp_dir
PRIV_KEY = os.path.join(os.getcwd(), '../common/grader.key')
CERT = os.path.join(os.getcwd(), '../common/grader.crt')
WWW = os.path.join(os.getcwd(), '../common/www')
CGI = os.path.join(os.getcwd(), '../common/cgi')


# battery of tests to run on the checkpoint
class Project1Test(unittest.TestCase):

    def __init__(self, test_name, grader):
        super(Project1Test, self).__init__(test_name)
        self.grader = grader

    # setUpClass doesn't work!?
    def setUp(self):
        self.out_string = ""
        self.repo = REPO_TEMPLATE % self.grader.andrewid
      	os.chdir(self.grader.tmp_dir)
        try:
            self.tearDown()
        except:
            pass
        self.git_clone(self.grader.root_repo)
        os.chdir(self.repo)
        self.repository = Repository('.git')
        commit = self.resolve_tag()
        self.git_checkout(commit.hex)
        self.ran = False
        self.port = random.randint(1025, 9999)
        self.tlsport = random.randint(1025, 9999)
        print '\nUsing ports: %d,%d' % (self.port, self.tlsport)


    def pAssertEqual(self, arg1, arg2):
        try:
            self.assertEqual(arg1, arg2)
        except Exception as e:
            self.print_str(traceback.format_stack()[-2])
            raise e

    def pAssertTrue(self, test):
        try:
            self.assertTrue(test)
        except Exception as e:
            self.print_str(traceback.format_stack()[-2])
            raise e

    def print_str(self, prt_str):
        print(prt_str)
        self.out_string += ("\n" + prt_str)

    def edit_notes(self, new_note):
        notef = self.grader.notes
        try:
            check_both('cat %s' % (notef), False)
            new_note = '\n'+new_note
        except:
            pass
        check_both('echo "%s\nGood." >> %s' % (new_note, notef), False)
        check_both('%s %s' % (self.grader.editor,notef))

    def confirm(self):
        print '-----------------------------------------------'
        test = raw_input('OK [y/n]? ').lower() in ['y','']
        self.pAssertTrue(test)

    def liso_name(self):
        name = './lisod'
        text = raw_input('liso name? ').strip()
        if text: name = text
        self.liso_name = name
        return name

    def get_path(self):
        path = None
        text = raw_input('path? ').strip()
        if text: path = text
        return path

    def get_port(self):
        port = self.port
        text = raw_input('port? ').strip()
        if text: port = int(text)
        self.port = port
        print port
        return port

    def get_tls_port(self):
        tls_port = self.tls_port
        text = raw_input('tls_port? ').strip()
        if text: tls_port = int(text)
        self.tls_port = tls_port
        print tls_port
        return tls_port

    def find_path(self, name, tree, path='./', d=0):
        if d == 15: return None
        name = name.lower().strip()

        # depth first...?
        for entry in tree:
            obj = self.repository[entry.oid]
            if isinstance(obj, Tree):
                obj = self.find_path(name, obj, os.path.join(path, entry.name), d+1)
                if obj:
                    return obj

        # now check this level...?
        for entry in tree:
            if entry.name.lower().strip() == name:
                return path
        return None

    def find_file(self, name, tree, d=0):
        if d == 15: return None
        name = name.lower().strip()

        # depth first...?
        for entry in tree:
            obj = self.repository[entry.oid]
            if isinstance(obj, Tree):
                obj = self.find_file(name, obj, d+1)
                if obj:
                    return obj

        # now check this level...?
        for entry in tree:
            if entry.name.lower().strip() == name:
                resolved = self.repository[entry.oid]
                if not isinstance(resolved, Blob):
                    continue
                return resolved
        return None

    def run_lisod(self, tree):
        path = self.get_path()
        liso = self.liso_name()
        port = self.get_port()
        tls_port = self.get_tls_port()
        if not path: path = self.find_path('Makefile', tree)
        print 'switching to: %s' % path
        os.chdir(path)
        check_both('make clean', False, False)
        check_output('make')
        self.ran = True
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        cmd = 'nohup %s %d %d %slisod.log %slisod.lock %s %s %s %s&' % (liso, port, tls_port, self.grader.tmp_dir, self.grader.tmp_dir, self.grader.www, self.grader.cgi, self.grader.priv_key, self.grader.cert)
        self.pAssertEqual(0, os.system(cmd))
        return liso

    def git_clone(self, repourl):
        with open('/dev/null', 'w') as f:
            self.pAssertEqual(0, check_call(['git','clone', repourl], stderr=f,
                             stdout=f))

    def git_checkout(self, commit_hex):
        with open('/dev/null', 'w') as f:
            self.pAssertEqual(0, 
                             check_call(['git','checkout','%s' % commit_hex],
                                        stdout=f, stderr=f))

    def resolve_tag(self):
        try:
            tag = self.repository.lookup_reference('refs/tags/checkpoint-%d' % self.grader.cp_num)
        except KeyError:
            try:
                tag = self.repository.lookup_reference('refs/tags/checkpoint_%d' % self.grader.cp_num)
            except KeyError:
                tag = self.repository.lookup_reference('refs/tags/checkpoint%d' % self.grader.cp_num)
        commit = self.repository[tag.target]
        while isinstance(commit, Tag): commit = self.repository[commit.target]
        return commit

    # test existence of tag in repo
    def test_tag_checkpoint(self):
        self.print_str('\n\n----- Testing Tag -----')
        self.repository.lookup_reference('refs/tags/checkpoint-%d' % self.grader.cp_num)

    # test turn in timestamp
    def test_timestamp(self):
        self.print_str('\n\n----- Testing Timestamp -----')
        commit = self.resolve_tag()
        self.print_str('ref/tags/checkpoint-%d: %s' % (self.grader.cp_num, commit.hex))
        self.print_str('Due: %s' % self.grader.due_date)
        utctime = datetime.datetime.utcfromtimestamp(commit.commit_time)
        utcoffset = datetime.timedelta(minutes=commit.commit_time_offset)
        timestamp = utctime + utcoffset
        self.print_str('Timestamp: %s' % timestamp)
        timediff = timestamp - self.grader.due_date
        if timediff.days >= 0 and\
           timediff.seconds > 0 or\
           timediff.microseconds > 0:
               raise ValueError

    # test readme.txt file up to snuff
    def test_readme_file(self):
        self.print_str('\n\n----- Testing readme.txt file -----')
        commit = self.resolve_tag()
        tree = commit.tree
        print '\n----- readme.txt -----'
        readme = self.find_file('readme.txt', tree)
        print readme.data,
        self.confirm()
        self.edit_notes('README:')

    # test vulnerabilities.txt up to snuff
    def test_vulnerabilities_file(self):
        self.print_str('\n\n----- Testing vulnerabilities.txt file -----')
        commit = self.resolve_tag()
        tree = commit.tree
        print '\n----- vulnerabilities.txt -----'
        vulnerable = self.find_file('vulnerabilities.txt', tree)
        print vulnerable.data,
        self.confirm()
        self.edit_notes('VULNERABILITIES:')

    # test tests.txt up to snuff
    def test_tests_file(self):
        self.print_str('\n\n----- Testing tests.txt file -----')
        commit = self.resolve_tag()
        tree = commit.tree
        print '\n----- tests.txt -----'
        tests = self.find_file('tests.txt', tree)
        print tests.data,
        self.confirm()
        self.edit_notes('TESTS:')

    # test Makefile up to snuff
    def test_Makefile_file(self):
        self.print_str('\n\n----- Testing Makefile file -----')
        commit = self.resolve_tag()
        tree = commit.tree
        print '\n----- Makefile -----'
        Makefile = self.find_file('Makefile', tree)
        print Makefile.data,
        self.confirm()
        self.edit_notes('MAKEFILE:')

    # test if source up to snuff
    def test_inspect_source(self):
        self.print_str('\n\n----- Inspect Source cod *.[c|h] -----')
        self.print_str(self.grader.source_reminder)
        self.pAssertEqual(0, check_call(['bash']))
        self.confirm()
        self.edit_notes('SOURCE:')

    # tests if make properly creates lisod...
    def test_lisod_file(self):
        self.print_str('\n\n----- Testing make -----')
        path = self.get_path()
        if not path: path = self.find_path('Makefile', commit.tree)
        os.chdir(path)
        check_output('make')
        self.pAssertTrue(os.path.exists('./lisod'))

    # send all test files to their server
    # get output, give 3 second timeout
    # check sha's of output
    def test_replays(self):
        self.print_str('\n\n----- Testing Replays -----')
        self.run_lisod(commit.tree)
        time.sleep(3)
        replays_dir = os.path.join(self.grader.tmp_dir, 'replays')
        if not os.path.exists(replays_dir):
            os.makedirs(replays_dir)
        files = os.listdir(replays_dir)
        num_passed = 0
        num_files = 0
        for fname in files:
            basename, extension = os.path.splitext(fname)
            if extension == '.test': 
                num_files += 1
                self.print_str('testing %s...' % fname)
                fname = os.path.join(self.grader.tmp_dir + 'replays', fname)
                outfile = os.path.join(self.grader.tmp_dir + 'replays', '%s_%s.out' % (basename, self.repo))
                command = 'ncat -i 1s localhost %d < %s > %s' % (self.port, fname, outfile)

                check_both(command, False, False)
                with open(os.path.join(self.grader.tmp_dir + 'replays', basename+'.out')) as f:
                    with open(outfile) as f2:
                        outhash = hashlib.sha256(f.read()).hexdigest()
                        out2hash = hashlib.sha256(f2.read()).hexdigest()
                        if outhash == out2hash:
                            self.print_str('ok')
                            num_passed += 1
                        else:
                            self.print_str('failed')
                check_both('rm %s' % outfile)
        self.print_str('passed %d of %d' % (num_passed, num_files))
        self.pAssertEqual(num_passed,num_files)

    def tearDown(self):
        os.chdir(self.grader.tmp_dir)
        shutil.rmtree(self.repo)
        if sys.exc_info() == (None, None, None): #test succeeded
            self.out_string += '\nok'
        else:
            self.out_string += '\nfailed'
        if self.out_string:
            check_both('echo "%s" >> %s' % (self.out_string, self.grader.results))
        if self.ran:
            print 'trying "killall %s"' % os.path.basename(self.liso_name)
            check_both('killall %s' % os.path.basename(self.liso_name), True, False)
            check_both('rm /tmp/lisod.log', True, False)
            check_both('rm /tmp/lisod.lock', True, False)
            #check_both('sudo /etc/init.d/networking restart')

class Project1Grader(object):
    def __init__(self, andrewid, cp_num, due_date, source_reminder):
        self.andrewid = andrewid
        self.cp_num = cp_num
        self.root_repo = ROOT_REPO_TEMPLATE % (andrewid, andrewid)
        self.tmp_dir = '/tmp/cp%d/' % self.cp_num
        self.due_date = due_date
        self.source_reminder = source_reminder
        self.notes = os.path.join(self.tmp_dir, '%s-cp%d.notes' % (self.andrewid, self.cp_num))
        self.results = os.path.join(self.tmp_dir, '%s-cp%d.results' % (self.andrewid, self.cp_num))
        check_both('rm %s' % self.notes, False, False)
        check_both('rm %s' % self.results, False, False)

        # set where we want resources to *end up*; then copy them there
        self.priv_key = os.path.join(self.tmp_dir, 'grader.key')
        self.cert = os.path.join(self.tmp_dir, 'grader.crt')
        self.www = os.path.join(self.tmp_dir, 'www/')
        self.cgi = os.path.join(self.tmp_dir, 'cgi/')

    def copyResources(self):
        shutil.copyfile(PRIV_KEY, self.priv_key)
        shutil.copyfile(CERT, self.cert)
        if not os.path.exists(self.www):
            shutil.copytree(WWW, self.www)
        if not os.path.exists(self.cgi):
            shutil.copytree(CGI, self.cgi)
            

    def prepareTestSuite(self):
    
        self.suite = unittest.TestSuite()
        self.suite.addTest(Project1Test('test_tag_checkpoint', self))
        self.suite.addTest(Project1Test('test_timestamp', self))
        self.suite.addTest(Project1Test('test_readme_file', self))
        self.suite.addTest(Project1Test('test_tests_file', self))
        self.suite.addTest(Project1Test('test_vulnerabilities_file', self))
        self.suite.addTest(Project1Test('test_Makefile_file', self))
        self.suite.addTest(Project1Test('test_inspect_source', self))
        self.suite.addTest(Project1Test('test_lisod_file', self))
        self.suite.addTest(Project1Test('test_replays', self))

    def runTests(self):
        print '\n\n----- Testing: %s -----' % (self.root_repo)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        self.copyResources()
        os.chdir(self.tmp_dir)
        unittest.TextTestRunner(verbosity=2).run(self.suite) 
        check_call(['touch', self.notes])
    
