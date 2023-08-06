from typing import Union
from dotenv import load_dotenv
import pyodbc # Python interface for ODBC API         https://github.com/mkleehammer/pyodbc
import os
from datetime import datetime
from datetime import timezone
import logging
import platform
import time

def get_connection(driver: Union[str, None]=None) -> pyodbc.Connection:
	"""Function for getting a connection using the configured environment.

	Allowed connection protocols include 'ActiveDirectoryIntegrated', 'ActiveDirectoryInteractive', 'ActiveDirectoryMsi' and 'SqlPassword'
	and is controlled by the 'IMBALANCE_LOG_PROTOCOL' environment parameter

	:param str driver: Configurable driver override, defaults to system determinable

	:returns: Read connection to the imbalance server
	:rtype: pyodbc.Connection
	"""
	try:
		load_dotenv(verbose=False, override=True)
	except:
		logging.info('Error in load_dotenv')

	server=os.environ['IMBALANCE_LOG_SERVER']
	database=os.environ['IMBALANCE_LOG_DATABASE']

	# Define the authentication protocol
	protocol=os.environ.get('IMBALANCE_LOG_PROTOCOL', 'SqlPassword')

	# Allow for driver override
	if driver is None:
		driver='ODBC Driver 17 for SQL Server'
		if platform.system() == 'Windows':
			driver='SQL Server'

	# Set the base connection string
	connection_string = 'DRIVER={' + driver + '};SERVER='+server+';DATABASE='+database

	# Update connection string for username and password if needed
	if protocol not in ['ActiveDirectoryIntegrated', 'ActiveDirectoryInteractive', 'ActiveDirectoryMsi']:
		username=os.environ['IMBALANCE_LOG_USERNAME']
		password=os.environ['IMBALANCE_LOG_PASSWORD']
		connection_string += ';UID=' + username + ';PWD=' + password
	else:
		connection_string += ';Authentication=' + protocol

		# Assign the UID for user assigned identities
		if protocol == 'ActiveDirectoryMsi':
			user_id = os.environ.get('IMBALANCE_LOG_ASSIGNED_UID', None)
			if user_id is not None:
				connection_string += ';UID=' + user_id

	# Connect to the database
	tries=0
	connect=False
	while tries < 5:
		try:
			connection = pyodbc.connect(connection_string)
			connect = True
			break
		except:
			tries = tries + 1
			time.sleep(0.1)
			logging.info('get_connection retry')
	# If we are not connected after 5 tries, retry once more and let the exception abort the operation
	if connect == False:
		connection = pyodbc.connect(connection_string)

	return connection

#
# Get a cursor for the logging database
#
def get_cursor():
    connection = get_connection()
    cursor = connection.cursor()
    return cursor

def log_files(filetype, filename, url, status, message):
    now = datetime.now(tz=timezone.utc)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('insert into files(dt, filetype, filename, url, status, message) values(?, ?, ?, ?, ?, ?)', now, filetype, filename, url, status, message)
    connection.commit()

def log_files_forecast(filetype, filename, url, status, message,starttime,filecount=0,elapsedtime=0,year='0000',month='00',day='00',forecast='0000',windpark=''):
    message = message[0:4000]
    now = datetime.now(tz=timezone.utc)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('insert into files(dt, filetype, filename, url, status, message, forecast,filecount,elapsedtime,year,month,day,starttime,windpark) values(?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?)', now, filetype, filename, url, status, message, forecast,filecount,elapsedtime,year,month,day,starttime,windpark)
    connection.commit()

def log(severity, message):
    now = datetime.now(tz=timezone.utc)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('insert into logs(dt, severity, message) values(?, ?, ?)', now, severity, message)
    connection.commit()

def log_application(severity, message, application):
    message = message[0:4000]
    now = datetime.now(tz=timezone.utc)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('insert into logs(dt, severity, message, application) values(?, ?, ?, ?)', now, severity, message, application)
    connection.commit()

def log_application_park(severity, message, application, windpark):
    message = message[0:4000]
    now = datetime.now(tz=timezone.utc)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('insert into logs(dt, severity, message, application, park) values(?, ?, ?, ?, ?)', now, severity, message, application, windpark)
    connection.commit()
# 
# Query the log database for a single row single column
#
def get_sql_value(sql):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    for row in cursor.fetchall():
        value = row.value
        break

    cursor.close()
    return value 
