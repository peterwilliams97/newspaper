from __future__ import division
"""
	Simple sql running on sqlite to demonstrate the 'department history' problem which is
		- expenses are incurred by employees
		- employees can change departments
		- expenses need to be charged against the department the employee belonged to 
		 	at the time the expense was incurred
	This is addressed by a table which records the department to which employees belonged
	at any given time.
	
	Created on 13/02/2011

	@author: peter
"""
from pysqlite2 import dbapi2 as sqlite

in_memory = True
if in_memory:
	db_name = ':memory:'
else:
	db_name = 'history.db'

# By convention, time starts at 1900-01-01 and ends at 2099-12-31

def create_tables(cursor):
	""" There are 3 tables
		- tbl_employee: Employees stored here
		- tbl_expense: Expenses stored here. Expenses are charged to employees
		- tbl_history: Employee department membership history stored here.
	"""
	cursor.execute("""CREATE TABLE tbl_employee (
		id INTEGER PRIMARY KEY,
		first_name VARCHAR(20) NOT NULL,
		last_name VARCHAR(20) NOT NULL,
		CONSTRAINT name UNIQUE (first_name, last_name)
		)""" )
	cursor.execute("""CREATE TABLE tbl_expense (
		id INTEGER PRIMARY KEY, 
		employee_id INTEGER,
		date DATE NOT NULL,
		cost DECIMAL(5,2) NOT NULL,
		description VARCHAR(40) NOT NULL,
		FOREIGN KEY (employee_id) REFERENCES tbl_employee(id),
		CONSTRAINT who_when UNIQUE (employee_id, date)
		)""" )
	cursor.execute("""CREATE TABLE tbl_history (
		id INTEGER PRIMARY KEY, 
		employee_id INTEGER,
		start_date DATE NOT NULL,
		end_date DATE NOT NULL,
		department VARCHAR(20) NOT NULL,
		FOREIGN KEY (employee_id) REFERENCES tbl_employee(id),
		CONSTRAINT who_when UNIQUE (employee_id, start_date)
		)""")

def add_employee(connection, cursor, first_name, last_name, department):
	""" Create an employee entry. 
	 	Note how the department goes in tbl_history 
	"""
	# the block under a 'with connection' is a python sqlite transaction
	with connection:
		cursor.execute("INSERT INTO tbl_employee VALUES (null, ?, ?)", (first_name, last_name))
		cursor.execute("""INSERT INTO tbl_history (employee_id, start_date, end_date, department) 
			SELECT tbl_employee.id, DATETIME('1900-01-01'), DATETIME('2099-12-31'), ? 
			FROM tbl_employee
			WHERE tbl_employee.first_name=? AND tbl_employee.last_name=?""",
			(department, first_name, last_name))

def add_expense(cursor, first_name, last_name, date, cost, description):
	""" Apply an expense of <cost, description> to employee <first_name, last_name>
		at time <date>
	"""
	cursor.execute("""INSERT INTO tbl_expense (id, employee_id, date, cost, description) 
		SELECT null, tbl_employee.id, ?, ?, ?
		FROM tbl_employee
		WHERE tbl_employee.first_name=? AND tbl_employee.last_name=?
		""", (date, cost, description, first_name, last_name))

def change_department(cursor, first_name, last_name, department, date):
	""" Change the department of employee <first_name, last_name> to <department>
		at time <date>
	"""
	# the block under a 'with connection' is a python sqlite transaction
	with connection:
		cursor.execute("""UPDATE tbl_history 
			SET end_date=?
			WHERE id = (SELECT tbl_history.id
				FROM tbl_employee JOIN tbl_history ON tbl_employee.id = tbl_history.employee_id
				WHERE tbl_employee.first_name=? AND tbl_employee.last_name=? AND tbl_history.end_date > DATETIME('2099-12-30'))
				""",(date,  first_name, last_name))
		# sqlite does not support SELECT INTO
		# http://stackoverflow.com/questions/2361921/select-into-statement-in-sqlite
		cursor.execute("""INSERT INTO tbl_history (id, employee_id, start_date, end_date, department) 
			SELECT null, tbl_employee.id, ?, DATETIME('2099-12-31'), ?
				FROM tbl_employee
				WHERE tbl_employee.first_name=? AND tbl_employee.last_name=?""",
			(date, department, first_name, last_name))

def make_test_data(connection, cursor, num_employees, num_departments, num_cycles, num_expenses_per_day):
	""" Make some test database entries for <num_employees> employees who cycle between
		<num_departments> departments <num_cycles> times and incur <num_expenses_per_day> expenses
		per day
	"""
	print 'make_test_data: num_departments=%d, num_employees=%d, num_cycles=%d, num_expenses_per_day=%d' \
	            % (num_departments, num_employees, num_cycles, num_expenses_per_day)
	print ' (should give expenses of %d * n for department n)' % (num_employees * num_cycles * num_expenses_per_day)
	
	# Functions to generate values for each field
	first_name = 'Darren'
	def get_name(employee_num):
		return 'Smith.%03d' % employee_num
	def get_date(day_num, fraction_of_day):
		d = day_num % 28
		m = (day_num//28)%12
		y = 2000 + day_num//28//12
		seconds = int(24*60*60*fraction_of_day)
		s = seconds % 60
		n = (seconds//60) % 60
		h = seconds//60//60
		return '%04d-%02d-%02d %2d:%2d:%2d' % (y, m+1, d+1, h, n, s)
	def get_cost(employee_num, department_num):
		return  department_num
	def get_department(department_num):
		return 'department %03d' % department_num
	def get_description(employee_num, department_num, department_change_num):
		return 'expense %03d:%03d for employee %03d' % (department_change_num, department_num, employee_num)
	
	# Create the employees
	department_change_num = 0
	for employee_num in range(num_employees): 
		add_employee(connection, cursor, first_name, get_name(employee_num), get_department(0))
	
	# Cycle each employee's department through all available num_cycles times
	for c in range(num_cycles):
		for department_num in range(0, num_departments): 
			for employee_num in range(num_employees): 
				change_department(cursor, first_name, get_name(employee_num), get_department(department_num), get_date(department_change_num, 0.0))
				for expense_num in range(num_expenses_per_day):
					add_expense(cursor, first_name, get_name(employee_num), get_date(department_change_num, (expense_num+1)/(num_expenses_per_day+2)), 
								get_cost(employee_num, department_num), get_description(employee_num,department_num,department_change_num))
			department_change_num += 1

def show_expenses_with_dates(cursor):
	column_headers = get_header('tbl_expense') + get_header('tbl_employee') + get_header('tbl_history')
	cursor.execute("""SELECT 
	tbl_expense.description, tbl_history.start_date, tbl_expense.date, tbl_history.end_date, tbl_history.department, tbl_history.id, tbl_expense.cost
		FROM tbl_expense 
		INNER JOIN tbl_employee ON tbl_expense.employee_id=tbl_employee.id
		INNER JOIN tbl_history ON tbl_expense.employee_id=tbl_history.employee_id
		WHERE tbl_history.start_date <= tbl_expense.date AND tbl_expense.date < tbl_history.end_date
		ORDER BY tbl_employee.id, tbl_expense.id
	""" )
	
	expenses = cursor.fetchall()
	print 'Expenses date range:', '-' * 30
	print '%4s:' % 'head', column_headers
	for i,e in enumerate(expenses):
		print '%4d:' % i, e

def show_expenses_by_department(cursor):
	""" Show expenses by department """ 
	cursor.execute("""SELECT 
	tbl_history.department, SUM(tbl_expense.cost)
		FROM tbl_expense 
		INNER JOIN tbl_employee ON tbl_expense.employee_id=tbl_employee.id
		INNER JOIN tbl_history ON tbl_expense.employee_id=tbl_history.employee_id
		WHERE tbl_history.start_date <= tbl_expense.date AND tbl_expense.date < tbl_history.end_date
		GROUP BY tbl_history.department
		ORDER BY tbl_history.department
	""" )
	
	expenses = cursor.fetchall()
	print 'Expenses by Department:', '-' * 30
	print 'Instance, Department,      Total Expenses'
	for i,e in enumerate(expenses):
		print '%6d:' % i, [str(e[0]), e[1]]

def show_employees(cursor):
	""" Show all the employees """ 
	cursor.execute("SELECT * FROM tbl_employee ORDER BY last_name, first_name")
	employees = cursor.fetchall()
	print 'Employees:', '-' * 30 
	for i,e in enumerate(employees):
		print '%4d:' % i, [str(x) for x in e]

if __name__ == '__main__':
	connection = sqlite.connect(db_name)
	cursor = connection.cursor()
	create_tables(cursor)
	make_test_data(connection, cursor, num_employees = 3, num_departments = 7, num_cycles = 4, num_expenses_per_day = 5)
	show_expenses_by_department(cursor)
	show_employees(cursor)
	cursor.close()
	connection.close()
	