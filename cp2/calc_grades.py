import os

RESULTS_DIR = './results'
GRADES_DIR = './grades'
EXPLANATION = '''Max score: 10 pts.
This is your raw score before any lateness penalty is applied.
Your score has two pieces:
    Style (5 pts): Was your code reasonably structured/commented? Did you describe your test suite? Vulnerabilities? README?
    HTTP  (5 pts): 6 tests were performed; you get 1 point for each test passed (with a max of 5 pts)'''

for file in os.listdir(RESULTS_DIR):
    current_file = os.path.join(RESULTS_DIR, file)
    name, extenstion = os.path.splitext(file)
    grade_file = os.path.join(GRADES_DIR, '%s.grade' % name)

    print name

    results = {}
    current_test = ''
    timestamp = ''
    with open(current_file, 'r') as f:
        for line in f:
            if current_test == 'Timestamp' and 'Timestamp' in line:
                timestamp = line.strip()
            if '----' in line:
                current_test = line.strip().split(' ')[2] 
            if line.strip() == 'ok' or line.strip() == 'failed':
                results[current_test] = (line.strip() == 'ok')
    f.closed

    style_score = 0
    http_score = 0
    late_string = ''
    try:
        if results['Tag']:
            if not results['Timestamp']:
                late_string = '\nLate: %s\n' % timestamp

            # style score
            if results['readme.txt']: style_score += 1
            if results['vulnerabilities.txt']: style_score += 1
            if results['Makefile']: style_score += 1
            if results['tests.txt']: style_score += 1
            if results['Source']: style_score += 1
            if style_score != 5: print '    style score: %d' % style_score

            # http score
            if results['Headers']: http_score += 1
            if results['HEAD']: http_score += 1
            if results['GET']: http_score += 1
            if results['POST']: http_score += 1
            if results['BW']: http_score += 1
            #if results['Apache']: http_score += 1
            http_score += 1  # free point for apache bench http 1.0 bug

            # don't accidentally give free points if their code didn't run
            if not results['Headers'] and not results['HEAD'] and not results['GET'] and not results['BW'] and not results['Apache']:
                http_score = 0
            if http_score > 5: http_score = 5
    except KeyError as e:
        print e

    with open(grade_file, 'w') as outf:
        outf.write('%d%s\n\n%s' % (style_score+http_score, late_string, EXPLANATION))
    outf.closed
