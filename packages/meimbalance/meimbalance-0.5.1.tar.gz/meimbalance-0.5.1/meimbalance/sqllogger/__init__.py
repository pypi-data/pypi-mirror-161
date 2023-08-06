from typing import Union
from dotenv import load_dotenv
import pyodbc # Python interface for ODBC API         https://github.com/mkleehammer/pyodbc
import os
from datetime import datetime
from datetime import timezone
import logging
import platform
import time

from meimbalance import sqllog

class sqllogger:
	def __init__(self):
		self.connection = sqllog.get_connection()

	def get_connection(self):
		return self.connection

	def close_connection(self):
		self.connection.close()

	def get_cursor(self):
		try:
			cursor = self.connection.cursor()
		except:
			print("ERROR in SQLLogClass: Cannot get cursor, will retry connect")
			self.connection = sqllog.get_connection()
			cursor = self.connection.cursor()

		return cursor

	def log_files(self, filetype, filename, url, status, message):
		now = datetime.now(tz=timezone.utc)
		cursor = self.get_cursor()
		cursor.execute('insert into files(dt, filetype, filename, url, status, message) values(?, ?, ?, ?, ?, ?)', now, filetype, filename, url, status, message)
		self.connection.commit()
		cursor.close()

	def log_files_forecast(self, filetype, filename, url, status, message,starttime,filecount=0,elapsedtime=0,year='0000',month='00',day='00',forecast='0000',windpark=''):
		message = message[0:4000]
		now = datetime.now(tz=timezone.utc)
		cursor = cursor = self.get_cursor()
		cursor.execute('insert into files(dt, filetype, filename, url, status, message, forecast,filecount,elapsedtime,year,month,day,starttime,windpark) values(?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?)', now, filetype, filename, url, status, message, forecast,filecount,elapsedtime,year,month,day,starttime,windpark)
		self.connection.commit()
		cursor.close()

	def log(self, severity, message):
		now = datetime.now(tz=timezone.utc)
		cursor = cursor = self.get_cursor()
		cursor.execute('insert into logs(dt, severity, message) values(?, ?, ?)', now, severity, message)
		self.connection.commit()
		cursor.close()

	def log_application(self, severity, message, application):
		message = message[0:4000]
		now = datetime.now(tz=timezone.utc)
		cursor = cursor = self.get_cursor()
		cursor.execute('insert into logs(dt, severity, message, application) values(?, ?, ?, ?)', now, severity, message, application)
		self.connection.commit()
		cursor.close()

	def log_application_park(self, severity, message, application, windpark):
		message = message[0:4000]
		now = datetime.now(tz=timezone.utc)
		cursor = self.get_cursor()
		cursor.execute('insert into logs(dt, severity, message, application, park) values(?, ?, ?, ?, ?)', now, severity, message, application, windpark)
		self.connection.commit()
		cursor.close()
	# 
	# Query the log database for a single row single column
	#
	def get_sql_value(self, sql):
		cursor = self.get_cursor()
		cursor.execute(sql)
		for row in cursor.fetchall():
			value = row.value
			break

		cursor.close()
		return value 

	def get_sql_value_parameter(self, sql, parameter):
		cursor = self.get_cursor()
		cursor.execute(sql, parameter)
		for row in cursor.fetchall():
			value = row.value
			break
		cursor.close()

		return value 
