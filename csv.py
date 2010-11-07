from __future__ import division
"""
manipulate .csv files
Clean advertisement detection trainging set file

Peter
16/05/2010
"""
import copy, os, time, sys, re

def validateMatrix(matrix):
	"""Check that all rows in matrix and same length"""
	assert(len(matrix) > 0)
	assert(len(matrix[0]) > 0)
	
	for i in range(1, len(matrix)):
		if not len(matrix[i]) == len(matrix[0]):
			print 'len(matrix[0]) =', len(matrix[0])
			print 'len row %3d = %3d' % (i, len(matrix[i]))
        assert(len(matrix[i]) == len(matrix[0]))

def validateMatrix2(matrix):
    """Check that all rows in matrix and same length and non-empty"""
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
     \s*?                # Allow arbitrary space before the comma.
    (?:,|$)            # Followed by a comma or the end of a string.
    ''', re.VERBOSE)

#csv_pattern = re.compile('(.*?)(?:,|$)')

def getCsvLine(line):
	#parts = line.strip().split(',')
	parts = csv_pattern.findall(line)
	return [p.strip() for p in parts]

def readCsvRaw(filename, remove_blank_lines = False, max_lines = 1000000): 
	""" Read a CSV file into a 2d array """
	f = open(filename, 'rt')
	entries = []
	for i in range(max_lines):
		line = f.readline().strip()
		if not line:
			break
		if remove_blank_lines and len(line) == 0:
			continue
		parts = getCsvLine(line)
		print i, parts
		entries.append(parts)
	f.close()
	print 'readCsvRaw:', filename, len(entries), len(entries[0])
	validateMatrix(entries)
	return entries

def readCsvLine(f, remove_blank_lines = True):
	""" Read a line of data from a .csv file """
	while True:
		line = f.readline().strip()
		if not line:
			return None
		if remove_blank_lines and len(line) == 0:
			continue
		return getCsvLine(line)
		
def readCsvGen(f, remove_blank_lines = True): 
	""" Generator to Read a CSV file as a list of list of string """
	while True:
		data = readCsvLine(f, remove_blank_lines)
		if not data:
			break
		yield data

def readCsvRaw2(filename, has_header, max_lines): 
    """ Read a CSV file into a header and 2d array """
    header = None
    entries = readCsvRaw(filename, True, max_lines)
    if has_header:
        header = entries[0]
        matrix = entries[1:]
    else:
        matrix = entries
    return (matrix, header)

def readCsvFloat2(filename, has_header): 
    "Reads a CSV file into a header and 2d array of float"
    header = None
    entries = readCsvRaw(filename)
    if has_header:
        header = entries[0]
        matrix = [[float(e) for e in row] for row in entries[1:]]
        print 'readCsvFloat:', filename, len(entries[1:]), len(entries[1])
    else:
        matrix = [[float(e) for e in row] for row in entries]
    return (matrix, header)    

def readCsvFloat(filename): 
    "Reads a CSV file into a 2d array of float"
    matrix, header = readCsvFloat2(filename, False)
    return matrix

def writeCsvRow(f, row):
	f.write(','.join(row) + '\n')

def writeCsv(filename, in_matrix, header = None):
    "Writes a 2d array to a CSV file"
    matrix = [header] + in_matrix if header else in_matrix
    print 'writeCsv:', filename, len(matrix), len(matrix[0])
    file(filename, 'w').write('\n'.join(map(lambda row: ','.join(map(str,row)), matrix)) + '\n')

  