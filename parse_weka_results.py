from __future__ import division
"""
Parse WEKA output

Created on 18/01/2011

@author: peter
"""

import sys, os, random, math, time, re, optparse, csv

def clean(str_arr):
    return [s.strip() for s in str_arr if len(s.strip()) > 0]

"""

=== Classifier model ===

JRIP rules:
===========

(Number.of.Unsuccessful.Grant <= 0) and (Number.of.Successful.Grant >= 1) and (Start.date <= 6.2) => Grant.Status=1 (447.0/17.0)
(Number.of.Unsuccessful.Grant <= 0) and (Number.of.Successful.Grant >= 1) and (Grant.Category.Code = 50A) => Grant.Status=1 (200.0/2.0)
(Number.of.Unsuccessful.Grant <= 0) and (Number.of.Successful.Grant >= 1) and (Start.date <= 6.72) => Grant.Status=1 (239.0/25.0)

Number of Rules : 43
"""
header_line = '=== Classifier model ==='
trailer_line = 'Number of Rules'

pattern_rule_line = r'(?P<rules>.*)=\>\s*(?P<class_key>\S+)=\s*(?P<class_val>\S+)\s*\((?P<num_true>\S+)/(?P<num_false>\S+)\)'
compiled_pattern_rule_line = re.compile(pattern_rule_line)

def get_rule_line(line):
    match = compiled_pattern_rule_line.search(line)
    if not match:
        return {}
    results = {}

    def add_key(key):
        results[key] = match.group(key).strip()

    add_key('rules')
    add_key('class_key')
    add_key('class_val')
    add_key('num_true')
    add_key('num_false')

    return results

if False:
    test_line = r'(Start.date <= 6.89) and (Start.date >= 6.63) and (Start.date <= 6.64) => Grant.Status=1 (18.0/1.0)'
    test_results = get_rule_line(test_line)
    print test_line
    print test_results
    exit()

pattern_rule = r'\((?P<key1>\S+)\s+(?P<relation>\S+)\s+(?P<key2>\S+)\)'
compiled_pattern_rule = re.compile(pattern_rule)

def get_one_rule(part):
    match = compiled_pattern_rule.search(part)
    if not match:
        return None

    results = {}

    def add_key(key):
        results[key] = match.group(key).strip()

    add_key('key1')
    add_key('relation')
    add_key('key2')

    return (results['key1'], results['key2'], results['relation'])

if False:
    test_rule = r'(Start.date <= 6.89)'
    test_results = get_one_rule(test_rule)
    print '"' + test_rule + '"'
    print test_results
    exit()

def get_rules(line):
    results = get_rule_line(line)
    if results.has_key('rules'):
        parts = clean(results['rules'].split('and'))
        if len(parts) > 0:
            keys =  set(x for x in [get_one_rule(p) for p in parts] if x)
            rules = {}
            for k in keys:
                num_true =float(results['num_true'])
                num_false = float(results['num_false'])
                rules[k] = (num_true+ num_false, abs(math.log(num_true+1) - math.log(num_false+1)) )
            return rules
    return None

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print 'usage:', sys.argv[0], '<file name>'
        exit()

    filename = sys.argv[1]
    data = file(filename, 'rt').read()
    file_lines = [x.strip() for x in data.split('\n') if len(x.strip()) > 0]

    all_rules = {}
    in_data = True
    for line in file_lines:
        if header_line in line:
            in_data = True
        elif trailer_line in line:
            break
        elif in_data:
            rules = get_rules(line)
            if rules:
                if False:
                    print line
                    print get_rules(line)
                for k in rules.keys():
                    if not all_rules.has_key(k) or rules[k] > all_rules[k]:
                         all_rules[k] = rules[k]

    print 'all_rules =', all_rules
    for i,k in enumerate(sorted(list(all_rules.keys()), key = lambda k: (-all_rules[k][0],all_rules[k][1]))):
        print '%3d: %3d %3.1f' % (i, int(all_rules[k][0]), all_rules[k][1]), k

    exit()

    out_filename = filename + '.csv'
    out_lines = ['Grant.Application.ID,Grant.Status,Success']
    for k in sorted(results.keys()):
        r = results[k]
        out_lines.append(','.join([str(x) for x in [k, r['prob1'], r['predicted1']]]))
    out_data = '\n'.join(out_lines)
    file(out_filename, 'wt').write(out_data)
