from __future__ import division
"""
manipulate .csv files
Clean advertisement detection trainging set file

Peter
16/05/2010
"""
import copy, os, time, sys, re, misc

def validateMatrix(matrix):
	""" Check that all rows in matrix and same length"""
	assert(len(matrix) > 0)
	assert(len(matrix[0]) > 0)
	
	for i in range(1, len(matrix)):
		if not len(matrix[i]) == len(matrix[0]):
			print 'len(matrix[0]) =', len(matrix[0])
			print 'len row %3d = %3d' % (i, len(matrix[i]))
        assert(len(matrix[i]) == len(matrix[0]))

def validateMatrix2(matrix):
    """ Check that all rows in matrix and same length and non-empty"""
    validateMatrix(matrix)
    for i,row in enumerate(matrix):
        for j,val in enumerate(row):
            if len(val) == 0:
                print 'empty cell', i, j        

def anyNotBlank(row):
	notBlank = False
	for e in row:
		if len(e) > 0:
			return True
	return False

# Based on http://stackoverflow.com/questions/2212933/python-regex-for-reading-csv-like-rows
csv_pattern = re.compile(r'''
   \s*?                # Any whitespace.
    (                  # Start capturing here.
      \s*? 
      |
      [^,"']+?         # Either a series of non-comma non-quote characters.
      |                # OR
      "(?:             # A double-quote followed by a string of characters...
          [^"\\]|\\.   # That are either non-quotes or escaped...
       )*?              # ...repeated any number of times.
      "                # Followed by a closing double-quote.
      |                # OR
      '(?:[^'\\]|\\.)*?'# Same as above, for single quotes.
     )                  # Done capturing.
   # \s*?                 # Allow arbitrary space before the comma.
    (?:\s*? ,|$)            # Followed by a comma or the end of a string.
    ''', re.VERBOSE)

#csv_pattern = re.compile('(.*?)(?:,|$)')

def getCsvLine(line):
	#parts = line.strip().split(',')
	parts = csv_pattern.findall(line)
	parts = [p.strip() for p in parts]
	while parts[-1] == '':
		parts = parts[:-1]
	return parts

def readCsvLine(f, remove_blank_lines = True):
	""" Read a line of data from a .csv file """
	while True:
		line = f.readline().strip().rstrip(',').rstrip()
		if not line:
			return None
		if remove_blank_lines and len(line) == 0:
			continue
		#print line
		assert(line[-1] != ',')
		return getCsvLine(line)

def readCsvGen(f, remove_blank_lines = True): 
	""" Generator to Read a CSV file as a list of list of string """
	while True:
		data = readCsvLine(f, remove_blank_lines)
		if not data:
			break
		yield data

def readCsv(filename, has_header = True): 
	""" Read a CSV file into a 2d array. 1st row is optionally returned in header 1d array """
	f = open(filename, 'rt')
	if has_header:
		header = readCsvLine(f)
	entries = [row for row in readCsvGen(f)]
	f.close()
	return (entries, header)

def readCsvAsDict(filename): 
	""" Read a CSV file into a dict with keys for each column header the columns as values (lists) """
	entries, header = readCsv(filename, True)
	columns = misc.transpose(entries)
	return dict(zip(header,columns)), len(entries)

def writeCsvRow(f, row):
	for s in row:
		if not isinstance(s, str):
			print len(row)
			print type(s)
			print 'bad type: exiting'
			exit()
		assert(isinstance(s, str))
		
	line = ','.join(row).strip()
	assert(line[-1] != ',')
	f.write(line + '\n')

def writeCsv(filename, in_matrix, header = None):
	"Writes a 2d array to a CSV file"
	matrix = [header] + in_matrix if header else in_matrix
	print 'writeCsv:', filename, len(matrix), len(matrix[0])
	f = open(filename, 'w')
	for row in matrix:
		writeCsvRow(f, row)
	f.close()

def writeCsvDict(filename, list_dict, sorted_keys = None):
	""" Writes a dict of lists where key is header and lists are columns of values """
	if not sorted_keys:
		sorted_keys = sorted(list_dict.keys())
	num_rows = len(list_dict[sorted_keys[0]])
	matrix = []
	for i in range(num_rows):
		 matrix.append([list_dict[k][i] for k in sorted_keys])
	writeCsv(filename, matrix, sorted_keys)

  