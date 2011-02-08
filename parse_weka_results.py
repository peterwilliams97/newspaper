from __future__ import division
"""
Parse WEKA output

Created on 18/01/2011

@author: peter
"""

import sys, os, random, math, time, re, optparse, csv, misc

DO_COMPOUND_RULES = True

def clean(str_arr):
    return [s.strip() for s in str_arr if len(s.strip()) > 0]

global_number = 0
def get_incrementing_number_():
    global global_number
    global_number += 1
    return global_number

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
    test_line = r'(Number.of.Unsuccessful.Grant <= 0) and (Contract.Value.Band...see.note.A = A) => Grant.Status=1 (506.0/82.0)'
    test_results = get_rule_line(test_line)
    print test_line
    print test_results
    exit()

pattern_rule = r'\((?P<attr>\S+)\s+(?P<relation>\S+)\s+(?P<val0>\S+)\)'
compiled_pattern_rule = re.compile(pattern_rule)

def string_to_rule(string):
    """ Parse a string and convert it to a rule (attr, relation, val0) """
    match = compiled_pattern_rule.search(string)
    if not match:
        return None

    results = {}

    def add_key(key):
        results[key] = match.group(key).strip()

    add_key('attr')
    add_key('relation')
    add_key('val0')

    return (results['attr'], results['relation'], results['val0'])

def rule_to_string(rule):
    """ Convert a rule (attr, relation, val0) to a string """
    attr, relation, val0 = rule
    return ''.join([attr, relation, val0])

def compound_rule_to_string(compound_rule):
    """ Convert a compound rule [(rule1) and (rule2) and ...]  to a string """
    return ' and '.join(['(' + rule_to_string(rule) + ')' for rule in compound_rule])

if False:
    test_rule = r'(Start.date <= 6.89)'
    test_rule = r'(Contract.Value.Band...see.note.A = A)'
    test_results = string_to_rule(test_rule)
    print '"' + test_rule + '"'
    print test_results
    exit()

def get_rules(line_num, line):
    results = get_rule_line(line)
    if results.has_key('rules'):
        parts = clean(results['rules'].split(' and '))
        if len(parts) > 0:
            keys =  set(x for x in [string_to_rule(p) for p in parts] if x)
            rules = {}
            for k in keys:
                num_true = int(float(results['num_true']))
                num_false = int(float(results['num_false']))
                rules[k] = (line_num, num_true, num_false)
            return rules
    return None

if False:
    test_line = r'(Start.date <= 6.89) and (Start.date >= 6.63) and (Start.date <= 6.64) => Grant.Status=1 (18.0/1.0)'
    test_line = r'(Number.of.Unsuccessful.Grant <= 0) and (Contract.Value.Band...see.note.A = A) => Grant.Status=1 (506.0/82.0)'
    test_rules = get_rules(test_line)
    print test_line
    for i,rule in enumerate(test_rules):
        print i, rule
    exit()

def get_all_attrs_vals_relations(all_rules):
    """ Return set of all attributes used in rules 
        all_rules: dict with rules as keys
    """
    all_attrs = set()
    all_vals = set()
    all_relations = set()
    for rule in all_rules.keys():
        attr, val, relation = rule
        all_attrs.add(attr)
        all_vals.add(val)
        all_relations.add(relation)
    return all_attrs, all_vals, all_relations

rule_evaluators = { 
    '=':  lambda val, val0: val == val0,
    '<=': lambda val, val0: val <= val0,
    '>=': lambda val, val0: val <= val0,
    '>':  lambda val, val0: val >  val0,
    '<':  lambda val, val0: val <  val0,
}

def evaluate_rule(rule, val):
    _, relation, val0 = rule
    return rule_evaluators[relation](val, val0)

def evaluate_compound_rule(compound_rule, vals):
    assert(len(compound_rule) == len(vals))
    n = len(vals)
    assert(n > 0)
    return all([evaluate_rule(compound_rule[i],vals[i]) for i in range(n)])

def get_rules_from_weka_results(weka_results_filename):

    data = file(weka_results_filename, 'rt').read()
    file_lines = [x.strip() for x in data.split('\n') if len(x.strip()) > 0]

    all_rules = {}
    compound_rules = []
    in_data = False
    for line_num, line in enumerate(file_lines):
        if header_line in line:
            in_data = True
        elif trailer_line in line:
            break
        elif in_data:
            rules = get_rules(line_num, line)
            if rules:
                if True:
                    print '%3d:'% line_num, line
                    print '%3d:'% line_num, rules.keys()
                for k in rules.keys():
                    if not all_rules.has_key(k) or rules[k][0] < all_rules[k][0]:
                         all_rules[k] = rules[k]
                compound_rules.append(rules.keys())
            if False:
                print '-'*30
                print line
                if rules:
                    for k,v in rules.items():
                        print k,v
                if 'Contract.Value.Band...see.note.A' in line:
                    exit()

    return all_rules, compound_rules

def get_sorted_rules_keys(all_rules):
    return sorted(list(all_rules.keys()), key = lambda k: all_rules[k][0])

def test_rules_from_weka_results(weka_results_filename):
    all_rules, compound_rules = get_rules_from_weka_results(weka_results_filename)
    sorted_keys = get_sorted_rules_keys(all_rules)

    for i,k in enumerate(sorted_keys[:25]):
        print '%3d:' % i, all_rules[k], k

    all_attrs, all_vals, all_relations = get_all_attrs_vals_relations(all_rules)
    print 'all_attrs =', len(all_attrs), sorted(list(all_attrs))
    print 'all_vals =', len(all_vals), sorted(list(all_vals))
    print 'all_relations =', len(all_relations), sorted(list(all_relations))
    print '-' * 40
    
    return all_rules

def get_short_name(filename):
    return os.path.splitext(os.path.basename(filename))[0].replace('.', '_')

#http://stackoverflow.com/questions/3920175/comparing-row-in-numpy-array
def unique_rows(data, classes):
    uniques = {}
    for i,row in enumerate(data):
        key = tuple(row)
        if not key in uniques:
            uniques[key] = [0,0]
        clazz = classes[i]
        uniques[key][clazz] += 1
    return uniques

def analyse_evals_dict(evals_dict, evals_header):
    """ Analyse an evals training dict. 
        By convention,class is in column 0
        The should be as many unique rules as permutations of attributes
    """
    print evals_header
    for i,key in enumerate(evals_header):
        print '%2d' % i, key
    classes = evals_dict[evals_header[0]]
    data = misc.transpose([evals_dict[k] for k in evals_header[1:]])
    uniques = unique_rows(data, classes)
    print '-' * 20
    for i,key in enumerate(sorted(uniques.keys(),key = lambda x: x[::+1])):
    #for i,key in enumerate(uniques.keys()):
        print '%2d: %4d,%4d' % (i, uniques[key][0], uniques[key][1]), key
    print '-'*20
    print 'total =', len(data)
    print 'unique =', len(uniques)
    print 'combinations =', 2 ** (len(evals_header)-1), 'from', len(evals_header)-1


if __name__ == '__main__':

    parser = optparse.OptionParser('usage: python ' + sys.argv[0] + ' [options] <weka results file name> <training file csv>')
    parser.add_option('-o', '--output', dest='output_dir', default='.', help='output directory')
    parser.add_option('-c', '--class', action='store_true', dest='has_class', default=False, help='has class values')
    parser.add_option('-r', '--rules', dest='num_rules', default='10', help='number of rules to include')

    (options, args) = parser.parse_args()
    if len(args) < 2:
        print parser.usage
        print 'options:', options
        print 'args:', args
        exit()

    weka_results_filename = args[0]
    data_file_csv = args[1]
    num_rules = int(options.num_rules)

    name = get_short_name(data_file_csv) + '.' + get_short_name(weka_results_filename) + '.knn.csv'
    knn_file_csv = os.path.join(options.output_dir, name)
    num_rules = int(options.num_rules)

    print 'options:', options
    print 'args:', args
    print 'has_class:', options.has_class
    print 'num_rules:', num_rules
    print 'weka_results_filename:', weka_results_filename
    print 'data_file_csv:', data_file_csv
    print 'output_dir:', options.output_dir
    print 'knn_file_csv:', knn_file_csv

    all_rules, compound_rules = get_rules_from_weka_results(weka_results_filename)
    sorted_keys = get_sorted_rules_keys(all_rules)
    
    attrs = sorted(list(set([attr for attr,_,_ in sorted_keys])))
    print ' attrs:', len(attrs), attrs

    data_dict, num_instances = csv.readCsvAsDict(data_file_csv)
    header = [k for k in sorted(data_dict.keys()) if k != 'Grant.Status']
    print 'header:', len(header), header

    for a in attrs:
        assert(a in header)

    evals_dict = {}
    if DO_COMPOUND_RULES:
        evals_header = [compound_rule_to_string(compound) for compound in compound_rules[:num_rules]]
        if False:
            for i,e in enumerate(evals_header):
                print i,e
    else:
        evals_header = [rule_to_string(rule) for rule in sorted_keys[:num_rules]]

    if options.has_class:
        print 'Adding class column'
        evals_dict['Grant.Status'] = data_dict['Grant.Status']
        evals_header = ['Grant.Status'] + evals_header
        
    if DO_COMPOUND_RULES:
        for i, compound in enumerate(compound_rules[:num_rules]):
            attrs = [attr for (attr, _, _) in compound]
            print attrs, compound
            val_rows = [[data_dict[attr][instance] for attr in attrs] for instance in range(num_instances)]
            evals = ['%.3f' % (2/(2+i)) if evaluate_compound_rule(compound, vals) else '0' for vals in val_rows]
            evals_dict[compound_rule_to_string(compound)] = evals
    else:
        for i, rule in enumerate(sorted_keys[:num_rules]):
            attr, _, _ = rule
            print attr, rule
            vals = data_dict[attr]
            evals = ['%.3f' % (2/(2+i)) if evaluate_rule(rule, val) else '0' for val in vals]
            evals_dict[rule_to_string(rule)] = evals
        
    if options.has_class:
        evals_dict0 = {}
        evals_dict0['Grant.Status'] = [int(s) for s in evals_dict['Grant.Status']] 
        if DO_COMPOUND_RULES:
            print 'compound_rules:', len(compound_rules)
            print 'num_rules:', num_rules
            for i, compound in enumerate(compound_rules[:num_rules]):
                attrs = [attr for (attr, _, _) in compound]
                val_rows = [[data_dict[attr][instance] for attr in attrs] for instance in range(num_instances)]
                evals = [1 if evaluate_compound_rule(compound, vals) else 0 for vals in val_rows]
                evals_dict0[compound_rule_to_string(compound)] = evals
        else:
            for i, rule in enumerate(sorted_keys[:num_rules]):
                attr, _, _ = rule
                vals = data_dict[attr]
                evals = [1 if evaluate_rule(rule, val) else 0 for val in vals]
                evals_dict0[rule_to_string(rule)] = evals
        analyse_evals_dict(evals_dict0, evals_header)

    csv.writeCsvDict(knn_file_csv, evals_dict, evals_header)

    if False:
        out_filename = filename + '.csv'
        out_lines = ['Grant.Application.ID,Grant.Status,Success']
        for k in sorted(results.keys()):
            r = results[k]
            out_lines.append(','.join([str(x) for x in [k, r['prob1'], r['predicted1']]]))
        out_data = '\n'.join(out_lines)
        file(out_filename, 'wt').write(out_data)
