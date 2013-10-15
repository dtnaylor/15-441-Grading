#!/usr/bin/python

import os

RESULTS_DIR = './results'
NOTES_DIR = './notes'
GRADES_DIR = './grades'
CP_GRADES_CSV = './checkpoint-grades.csv'

MESSAGE = '''Below is your raw score before any late penalty is applied.
If you have questions about your score or would like a regrade, please email
the course staff at staff-441@cs.cmu.edu.'''

TESTS = {

    #
    # HTTP 1.1  (15 pts)
    #
    # (additional 5 pts from CP2 added later)
    #
    'Headers':3,
    'HEAD':3,
    'GET':3,
    'pipelining':3,
    'Browser':3,

    #
    # TLS  (15 pts)
    #
    'TLS Browser':10,
    'TLS pipelining':5,

    #
    # CGI  (10 pts)
    #
    # 3 pts: test_cgi
    # 7 pts: test_blog
    #
    'CGI':3,
    'Blog':7,

    #
    # ROBUSTNESS  (10 pts)
    #
    'BW':2,
    'Bad PUT':1,
    'Bad Length Post':1,
    'Bad Ending GET':1,
    'Tests':3,
    'Replays':2,

    #
    # STYLE  (5 pts)
    #
    'Comments':5,

    #
    # CORE NETWORKING  (25 pts)
    #
    # (additional 5 pts from CP1 added later)
    #
    'Makefile':5,
    'README':5,
    'Modularity':5,
    'Vulnerabilities':5,
    'Tag':5,
    'Other':0,

    #
    # CHECKPOINTS  (20 pts)
    #
    'Checkpoint 1':10,
    'Checkpoint 2':10
}

DROPPED_TESTS = ['CGI']

def total_possible():
    total = 0
    for test in TESTS:
        total += TESTS[test]
    return total





##
##  Make dictionaries for cp1 and cp2 grades.
##
##  format of each line: andrewid,cp1score,cp2score
##
cp1 = {}
cp2 = {}
with open(CP_GRADES_CSV, 'r') as cpf:
    for line in cpf:
        vals = line.split(',')
        cp1[vals[0]] = int(vals[1])
        cp2[vals[0]] = int(vals[2].strip())
cpf.closed


for results_file in os.listdir(RESULTS_DIR):

    # Files and paths
    results_path = os.path.join(RESULTS_DIR, results_file)
    name, extenstion = os.path.splitext(results_file)
    grade_file = os.path.join(GRADES_DIR, '%s.grade' % name)

    # Per-student vars
    andrewid = name.split('-')[0]
    results = {}  # testname -> points earned
    timestamp = ''

    print andrewid

    ##
    ##  Parse results file
    ##
    current_test = ''
    with open(results_path, 'r') as resultsf:
        for line in resultsf:
            if current_test == 'Timestamp' and 'Timestamp' in line:
                timestamp = line.strip()

            if '----' in line:
                if 'Testing' in line:
                    current_test = line.strip().split('Testing ')[1].split(' ---')[0]
                else:
                    current_test = line.strip().split(' ')[2] # for 'Inspect Source'

            if line.strip() == 'ok' or line.strip() == 'failed':
                # We don't care about tests that aren't in the TESTS dict
                if current_test in TESTS:
                    if current_test in DROPPED_TESTS:  # full points
                        results[current_test] = TESTS[current_test]
                    else:  # all or nothing: ok => max points, failed => 0
                        results[current_test] = TESTS[current_test] if line.strip() == 'ok' else 0
    resultsf.closed


    ##
    ##  Parse notes file
    ##
    ## special lines in format:  ### Testname Points-earned
    ##
    notes_file = os.path.join(NOTES_DIR, '%s-cp3.notes' % andrewid)
    with open(notes_file, 'r') as notesf:
        for line in notesf:
            if '###' in line:
                vals = line.split(' ')
                results[vals[1]] = float(vals[2].strip())
    notesf.closed
    
    
    ##
    ##  Add checkpoint scores to results dict
    ## 
    results['Checkpoint 1'] = cp1[andrewid]
    results['Checkpoint 2'] = cp2[andrewid]


    ##
    ##   Add up how many points they earned
    ##
    score = 0
    details_str = ''

    for test in TESTS:
        possible = TESTS[test]
        earned = 0
        try:
            earned = results[test]
        except KeyError as e:
            print '\tKey Error: %s' % e
        score += earned
        details_str += '%s\t%g/%d\n' % (test.ljust(20), earned, possible)
    
    
    
    ##
    ##  Deal with late submissions
    ##
    timestamp_str = '%s' % timestamp
    if 'Late' in results:
        timestamp_str += '  (%d day(s) late)' % results['Late']
    else:
        timestamp_str += '  (on time)'


    ##
    ##  Write final score & breakdown to a grade file
    ##
    with open(grade_file, 'w') as gradef:
        gradef.write('%s\n\nTOTAL SCORE: %g/%d\n%s\n\nDETAILS:\n%s' % (MESSAGE, score, total_possible(), timestamp_str, details_str))
    gradef.closed
