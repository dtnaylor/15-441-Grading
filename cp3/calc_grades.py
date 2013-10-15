#!/usr/bin/python

import os

RESULTS_DIR = './results'
GRADES_DIR = './grades'
CP_GRADES_CSV = './checkpoint-grades.csv'
TESTS = {

    #
    # HTTP 1.1  (20 pts)
    # 
    # 5 points from CP2 (added later)
    # 3 points each for:
    #  test_HEAD_headers
    #  test_HEAD
    #  test_GET
    #  test_pipelining
    #  test_browser
    #
    'Headers':3,
    'HEAD':3,
    'GET':3,
    'pipelining':3,
    'Browser':3,

    #
    # TLS  (15 pts)
    # 
    # 10 pts: test_browser
    # 5 pts: tls pipelining
    #
    'TLS Browser':10,
    'TLS pipelining':5,

    #
    # CGI  (15 pts)
    #
    # 5 pts: test_cgi
    # 10 pts: test_blog
    #
    'CGI':5,
    'Blog':10,

    #
    # ROBUSTNESS  (10 pts)
    #
    # 2 pts: bw
    # 1 pt each: bad put, bad length, bad end
    # 5 pts: test cases
    #
    'BW':2,
    'Bad PUT':1,
    'Bad Length Post':1,
    'Bad Ending GET':1,
    'tests.txt file':5,

    #
    # STYLE  (5 pts)
    #
    # 1 pt each: readme, makefile, vulnerabilities, source, replay
    #
    'readme.txt file':1,
    'Makefile file':1,
    'vulnerabilities.txt file':1,
    'Source':1,
    'replay.[test|out] files':1
}





##
##  Make dictionaries for cp1 and cp2 grades. file contains lines like:
##
##  andrewid,cp1score,cp2score
##
cp1 = {}
cp2 = {}
with open(CP_GRADES_CSV, 'r') as cpf:
    for line in cpf:
        vals = line.split(',')
        cp1[vals[0]] = int(vals[1])
        cp2[vals[0]] = int(vals[2].strip())


for file in os.listdir(RESULTS_DIR):
    current_file = os.path.join(RESULTS_DIR, file)
    name, extenstion = os.path.splitext(file)
    grade_file = os.path.join(GRADES_DIR, '%s.grade' % name)
    andrewid = name.split('-')[0]

    print andrewid

    ##
    ##  Parse their results file
    ##
    results = {}
    current_test = ''
    timestamp = ''
    with open(current_file, 'r') as f:
        for line in f:
            if current_test == 'Timestamp' and 'Timestamp' in line:
                timestamp = line.strip()
            if '----' in line:
                if 'Testing' in line:
                    current_test = line.strip().split('Testing ')[1].split(' ---')[0]
                else:
                    current_test = line.strip().split(' ')[2] # for 'Inspect Source'

            if line.strip() == 'ok' or line.strip() == 'failed':
                results[current_test] = (line.strip() == 'ok')
    f.closed


    ##
    ##   Add up how many points the earned for each test
    ##
    score = 0
    score_str = ''
    late_string = '' if results['Timestamp'] else '\nLate: %s\n' % timestamp

    for test in TESTS:
        possible = TESTS[test]
        earned = 0
        try:
            earned = possible if results[test] else 0
        except KeyError as e:
            print '\tKey Error: %s' % e
        score += earned
        score_str += '%s\t%d/%d\n' % (test.ljust(24), earned, possible)
    
    
    #
    # CORE NETWORKING  (30 pts)
    #
    # 5 points from CP1 (added later)
    # 25 free points, to be manually decreased based on notes   TODO: figure this out
    # If the score is 0 so far, don't give them the free points --- assume
    # something was wrong with their submission
    #  
    core_score = 25 if score != 0 else 0
    score += core_score
    score_str += '%s\t%d/25\n' % ('Core Networking'.ljust(24), core_score)


    ##
    ##  Add in the checkpoint scores
    ## 
    score += cp1[andrewid]
    score_str += '%s\t%d/10\n' % ('Checkpoint 1'.ljust(24), cp1[andrewid])
    score += cp2[andrewid]
    score_str += '%s\t%d/10\n' % ('Checkpoint 2'.ljust(24), cp2[andrewid])


    ##
    ##  Write final score & breakdown to a grade file
    ##
    with open(grade_file, 'w') as outf:
        outf.write('TOTAL SCORE: %d/105%s\n\nDetails:\n%s' % (score, late_string, score_str))
    outf.closed
