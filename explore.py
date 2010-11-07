from __future__ import division
"""
Created on 06/11/2010

@author: peter
"""
import sys, os, csv

hearst_dir = r'\downloads\hearst'
model_dir = os.path.join(hearst_dir, 'Hearst_Challenge_Modeling_CSV_Files')
train_file_1 = os.path.join(hearst_dir, 'zip_plus4_data_1.csv')
train_file_2 = os.path.join(hearst_dir, 'zip_plus4_data_2.csv')
train_file_3 = os.path.join(hearst_dir, 'zip_plus4_data_3.csv')
sales_mo = os.path.join(model_dir, 'sales_mo_dataset.csv')
store_mo = os.path.join(model_dir, 'store_mo_dataset.csv')

def sample(filename):
    matrix, header = csv.readCsvRaw2(filename, True, 8)
    print 'filename', filename
    print 'header', header
    print 'matrix', matrix
    
    print '---------------------------------------'
    print zip(header, matrix[1])
    for x in sorted(zip(header, *matrix)):
        if len (x[0]):
            print x
    
    print '======================================='
    return header

def round(x):
    return int(x+0.5)

def getAllValueCounts(filename, keys):
    print 'getAllValueCounts', filename, keys
    f = open(filename, 'rt')
    header = csv.readCsvLine(f)
    data = csv.readCsvGen(f)
    print header

    column_index = dict(zip(keys, [header.index(k) for k in keys]))
    counts = dict(zip(keys, [{} for k in keys]))
    print 'indexes', column_index
    print ' counts', counts

    num_lines = 0
    for row in data:
        num_lines += 1
        for k in keys:
            val = row[column_index[k]]
            counts[k][val] = counts[k].get(val,0) + 1

    print filename, num_lines, 'lines'
    for k in keys:
        val = counts[k]
        print k, len(val), val
        total = sum(val.values())
        cumulative = 0.0
        if True:
            for v in sorted(val.keys(), key = lambda x: -val[x]):
                percent = val[v]*100.0/total
                cumulative += percent
                print '%5s %8d %3d%% %3d%%' % (v, val[v], round(percent), round(cumulative))
        print '%5s %8d %3d%% %3d%%' % ('total', total, round(sum([v*100.0/total for v in val.values()])), round(cumulative))
    f.close()
    return counts

def getAllStats(filename, keys):
    print 'getHiLo', filename, keys
    f = open(filename, 'rt')
    header = csv.readCsvLine(f)
    data = csv.readCsvGen(f)
    print header

    column_index = dict(zip(keys, [header.index(k) for k in keys]))
    stats = dict(zip(keys, [{'lo':sys.maxint, 'hi':-sys.maxint, 'mean': 0} for k in keys]))
    print 'indexes', column_index
    print ' stats', stats

    num_rows = 0
    for row in data:
        num_rows += 1
        for k in keys:
            val = float(row[column_index[k]])
            s = stats[k]
            if stats[k]['lo'] < val:
                stats[k]['lo'] = val
            if stats[k]['hi'] > val:
                stats[k]['hi'] = val
            stats[k]['mean'] += val
    for k in keys:
        stats[k]['mean'] = stats[k]['mean']/num_rows 

    print filename, num_rows, 'rows'
    for k in keys:
        print k, stats[k]
    f.close()
    return stats

def getStats(filename):
    f = open(filename, 'rt')
    header = csv.readCsvLine(f)
    lines = csv.readCsvGen(f)
    num_rows = 0
    for l in lines:
        num_rows += 1
    print filename, num_rows, 'lines'
    f.close()

if __name__ == '__main__':
    if False:
        h1 = sample(train_file_1)
        h2 = sample(train_file_2)
        h3 = sample(train_file_3)
    
    
    if True:
        store_h = sample(store_mo)
    if True:
        sales_h = sample(sales_mo)
    if False:
        getStats(store_mo)
    if False:
        getStats(sales_mo)
    
    getAllValueCounts(store_mo, ['STATE'])
    getAllValueCounts(sales_mo, ['wholesaler_key'])
    
    getAllStats(sales_mo, ['dollar_volume', 'sales', 'returns'])

    
    if False:
        print zip(h1, h2)
        print [x1 == x2 for x1,x2 in zip(h1,h2)]
        print '======================================'
    
    if False:
        groups = {}
        for h in h1:
            parts = h.split('_')
            if len(parts) >= 2:
                groups[parts[0]] = []
            else:
                groups[h] = [h]
        for h in h1:
            parts = h.split('_')
            if len(parts) >= 2:
                groups[parts[0]].append(h) 
             
        for k,v in sorted(groups.items()):
            print k, len(v), v      
        