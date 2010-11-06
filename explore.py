from __future__ import division
"""
Created on 06/11/2010

@author: peter
"""
import os, csv

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
    
if __name__ == '__main__':
    if False:
        h1 = sample(train_file_1)
        h2 = sample(train_file_2)
        h3 = sample(train_file_3)
    
    if True:
        store_h = sample(store_mo)
    sales_h = sample(sales_mo)

    
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
        