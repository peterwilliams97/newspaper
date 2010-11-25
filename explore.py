from __future__ import division
"""
Created on 06/11/2010

@author: peter
"""
import sys, os, csv

def insertSuffix(path, suffix):
    return os.path.splitext(path)[0] + '.' + suffix + os.path.splitext(path)[1]

hearst_dir = r'\downloads\hearst'
model_dir = os.path.join(hearst_dir, 'Hearst_Challenge_Modeling_CSV_Files')

train_file_1 = os.path.join(hearst_dir, 'zip_plus4_data_1.csv')
train_file_2 = os.path.join(hearst_dir, 'zip_plus4_data_2.csv')
train_file_3 = os.path.join(hearst_dir, 'zip_plus4_data_3.csv')

# 10,929,954 rows
sales_mo = os.path.join(model_dir, 'sales_mo_dataset.csv')

store_mo = os.path.join(model_dir, 'store_mo_dataset.csv')

# 10,768,254 rows
sales_mo_filtered = insertSuffix(sales_mo, 'filtered')
sales_mo_histo = insertSuffix(sales_mo_filtered, 'histo')


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

def getAllStats(filename, keys, max_rows = sys.maxint):
    print 'getAllStats', filename, keys
    f = open(filename, 'rt')
    header = csv.readCsvLine(f)
    data = csv.readCsvGen(f)
    print header

    column_index = dict(zip(keys, [header.index(k) for k in keys]))
    stats = dict(zip(keys, [{'lo':sys.maxint, 'hi':-sys.maxint, 'mean': 0} for k in keys]))

    num_rows = 0
    for row in data:
        for k in keys:
            val = float(row[column_index[k]])
            s = stats[k]
            if stats[k]['lo'] > val:
                stats[k]['lo'] = val
            if stats[k]['hi'] < val:
                stats[k]['hi'] = val
            stats[k]['mean'] += val
        num_rows += 1
        if num_rows > max_rows:
            break
    for k in keys:
        stats[k]['mean'] = stats[k]['mean']/num_rows 

    print filename, num_rows, 'rows'
    for k in keys:
        print k, stats[k]
    f.close()
    return stats

def binarySearch(levels, x):
    """ Find bin containing x
        bin[i] is for level[i]..level[i+1]
    """
    lo = 0
    hi = len(levels) - 2
    #print 'binarySearch', x, lo, hi, levels
    while lo < hi:
        #print lo, hi, levels[lo], levels[hi]
        mid = (lo+hi)//2
        midval0 = levels[mid]
        midval1 = levels[mid+1]
        if midval1 < x:
            lo = mid+1
        elif midval0 > x:
            hi = mid
        else:
            return mid
    raise RuntimeError('Cannot be here')

def populateHistogram(filename, histo, max_rows):
    print 'populateHistogram', histo.keys()
    f = open(filename, 'rU')
    header = csv.readCsvLine(f)
    data = csv.readCsvGen(f)
    column_index = dict(zip(header, [header.index(k) for k in header]))

    for i,row in enumerate(data):
        for k in histo.keys():
            x = float(row[column_index[k]])
            bin = binarySearch(histo[k]['levels'], x)
            histo[k]['counts'][bin] += 1
        if i >= max_rows:
            break
    f.close()
    
    sales_histo = histo['sales']
    for i,count in enumerate(sales_histo['counts']):
        print '%4d: %7d %8.2f %8.2f' % (i, count, sales_histo['levels'][i], sales_histo['levels'][i+1]-sales_histo['levels'][i])
        assert(sales_histo['levels'][i+1] >= sales_histo['levels'][i])

def makeHistogram(histo, num_bins):
    """ Make a new histogram with <num_bins> based on <histo> """
    print 'makeHistogram', num_bins,histo.keys()
    new_histo = {}
    for k,his in histo.items():
        his = histo[k]
        for i,count in enumerate(his['counts']):
            print '%4d: %7d %9.2f %9.2f %7.2f ' % (i, count, his['levels'][i],his['levels'][i+1], his['levels'][i+1]-his['levels'][i])
            assert(his['levels'][i+1] >= his['levels'][i])
            
        new_histo[k] = {}
        old_num_bins = len(his['counts'])
        sum_counts = sum(his['counts'])
        new_histo[k]['levels'] = []  # his['levels'][:1]
        for n,count in enumerate(his['counts']):
            num_sub_bins = max(1, int((count/sum_counts)*num_bins))
            width = his['levels'][n+1] - his['levels'][n]
            #print ' *', num_sub_bins, width
            for i in range(num_sub_bins):
                new_histo[k]['levels'].append(histo[k]['levels'][n]+ i*width)
        new_histo[k]['levels'].append(histo[k]['levels'][n])
        
        new_histo[k]['counts'] = [0 for i in range(len(new_histo[k]['levels'])-1)]
        print k, len(new_histo[k]['counts']), len(new_histo[k]['levels']), new_histo[k]['levels']
        his = new_histo[k]
        for i,count in enumerate(his['counts']):
            print '%4d: %7d %9.2f %9.2f %7.2f ' % (i, count, his['levels'][i],his['levels'][i+1], his['levels'][i+1]-his['levels'][i])
            assert(his['levels'][i+1] >= his['levels'][i])
    return new_histo

def getHistogram(filename, keys, stats, max_rows = sys.maxint):
    """ Return a histogram of the form
        [(upper<i>, count<i>) for i=1..N]
    """
    print 'getHistogram', filename, keys, stats

    # Max equal width bins
    num_bins = 10 
    histo = dict(zip(keys, 
                 [{'counts':[0 for i in range(num_bins)],
                   'levels':[stats[k]['lo'] + i *(stats[k]['hi']-stats[k]['lo']) for i in range(num_bins+1)]}
                  for k in keys]))
    populateHistogram(filename, histo, max_rows)
    
    for num_bins in [20,40]:
        histo = makeHistogram(histo, num_bins)
        populateHistogram(filename, histo, max_rows)
        
    return histo

    for i,row in enumerate(data):
        for k in keys:
            val = float(row[column_index[k]])
            bin = int((num_bins-1)*(val-stats[k]['lo'])/(stats[k]['hi']-stats[k]['lo']))
            histo[k][bin] += 1
        if i >= max_rows:
            break
    f.close()
    num_rows = i
    print 'read', num_rows, 'to make', num_bins, 'equal depth bins'
    for k in keys:
        print k, stats[k]['lo'], stats[k]['hi'], histo[k]

    num_equal = 10
    equal_depth = dict(zip(keys, [[None for i in range(num_equal)] for k in keys]))

    # Make equal depth bins

    for k in keys:
        bin_num = 0
        cumulative = 0
        for i in range(num_equal):
            while cumulative/num_rows < i/num_equal:
               cumulative += histo[k][bin_num]
               bin_num += 1
            equal_depth[k][i] = [cumulative, 0]
            # print '  ', i, bin_num, cumulative
        print 'bin_num', bin_num, ' len(histo)', len(histo[k])
        assert(bin_num <= len(histo[k])-1)

    if False:
        f = open(filename, 'rU')
        header = csv.readCsvLine(f)
        data = csv.readCsvGen(f)
    
        for k in keys:
            print k, stats[k]['lo'], stats[k]['hi'], equal_depth[k]
        for i,row in enumerate(data):
            for k in ['sales']: # keys:
                val = float(row[column_index[k]])
                bin_num = binarySearch(equal_depth[k], val)
                equal_depth[k][bin_num][1] += 1
                print bin_num, val
            if i >= max_rows:
                break
        f.close()
        
        for k in keys:
            print '&&', k, len(equal_depth[k])
    
        return equal_depth

def filterBadValues(in_filename, out_filename, keys):
    print 'filterBadValues', in_filename, out_filename, keys
    fin = open(in_filename, 'rt')
    fout = open(out_filename, 'wt')

    header = csv.readCsvLine(fin)
    csv.writeCsvRow(fout, header)
    print header

    data = csv.readCsvGen(fin)

    column_index = dict(zip(keys, [header.index(k) for k in keys]))

    num_rows = 0
    num_bad = 0
    for row in data:
        bad_row = False
        for k in keys:
            val = float(row[column_index[k]])
            if val < 0:
                bad_row = True
                num_bad += 1
        if not bad_row:
            csv.writeCsvRow(fout, row)
        num_rows += 1

    fin.close()
    fout.close()

    print in_filename, num_rows, 'rows'
    print out_filename, num_rows - num_bad, 'rows'

def sampleCsv(in_filename, out_filename, ratio):
    """ Sample a csv file. """
    print 'sampleCsv', in_filename, out_filename, ratio
    fin = open(in_filename, 'rt')
    fout = open(out_filename, 'wt')

    header = csv.readCsvLine(fin)
    print 'header:', header
    csv.writeCsvRow(fout, header)


    data = csv.readCsvGen(fin)

    num_sampled = 0

    for irow,row in enumerate(data):
        if irow % 100000 == 0:
            print (irow,num_sampled),
        if num_sampled < ratio * irow:
            csv.writeCsvRow(fout, row)
            num_sampled += 1
          
    print

    fin.close()
    fout.close()

    print in_filename, irow, 'rows'
    print out_filename, num_sampled, 'rows'
    
    if True:
        fin = open(out_filename, 'rt')
        header = csv.readCsvLine(fin)
        data = csv.readCsvGen(fin)
        for irow,row in enumerate(data):
            if len(row) != len(header):
                print irow, len(row), row, len(header), header
            assert(len(row) == len(header))
        fin.close()
    
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
    
    if False:
        store_h = sample(store_mo)
    if False:
        sales_h = sample(sales_mo)
    if False:
        getStats(store_mo)
    if False:
        getStats(sales_mo)

    if False: 
        filterBadValues(sales_mo, sales_mo_filtered, ['sales'])
        exit()

    if False:
        getAllValueCounts(store_mo, ['STATE'])
        getAllValueCounts(sales_mo, ['wholesaler_key'])

    measured_keys = ['dollar_volume', 'sales', 'returns']
    if False:
        stats = getAllStats(sales_mo_filtered, measured_keys)
    """
    dollar_volume {'lo': 0.0, 'hi': 14140.078125, 'mean': 26.854670163087913}
    sales {'lo': 0.0, 'hi': 2952.0, 'mean': 7.0670377017481201}
    returns {'lo': -332.0, 'hi': 13172.0, 'mean': 10.143592173810164}
    """
    # 10,768,254 rows
    sales_mo_filtered_rows = 10768254
    
    sample_rows = 10000
    sales_mo_sampled = insertSuffix(sales_mo_filtered, 'sample.%d'% sample_rows)
    sampleCsv(sales_mo_filtered, sales_mo_sampled, sample_rows/sales_mo_filtered_rows)

    stats = {'dollar_volume': {'lo': 0.0,    'hi': 14140.078125, 'mean': 26.854670163087913},
                     'sales': {'lo': 0.0,    'hi': 2952.0, 'mean': 7.0670377017481201},
                   'returns': {'lo': -332.0, 'hi': 13172.0, 'mean': 10.143592173810164}
            }
    if False:
        histo = getHistogram(sales_mo_filtered, measured_keys, stats, 20000)
        exit()
    if False:
        keys = [k+':'+t for k in measured_keys for t in ['level','number']]
        columns = [histo[k][i] for k in measured_keys for i in [0,1]]
        print len(columns), [len(c) for c in columns]
        histo_cols = dict(zip(keys, columns))
    if False:
        histo_cols = {}
        for k in measured_keys: 
            for i in [0,1]:
                ck = k + ' ' + ['level','number'][i]
                histo_cols[ck] = [histo[k][n][i] for n in range(len(histo[k]))]
        csv.writeCsvDict(sales_mo_histo, histo_cols)

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
        