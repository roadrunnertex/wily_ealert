#! python
#! -*- coding: utf-8 -*-

"""
Database class to interface with SQLite3 database
"""

__author__ = "Dan Newburg"
__version__ = "1.1.3"
__maintainer__ = "Dan Newburg"
__email__ = "dan.newburg@gmail.com"
__status__ = "Development"

from logger import Logger
import os
import sqlite3
import sys

class Database:
	def __init__(self,db_name,table_name, debug, log_path):
		"""Initializes information pertaining to a SQLite database"""
		self.db_name = db_name
		self.table_name = table_name
		self.db_connection = None
		self.db_cursor = None
		self.logger = Logger(self.__class__.__name__, debug, log_path).get_logger()

	def connect_to_database(self):
		try:
			self.db_connection = sqlite3.connect(self.db_name, timeout=30)
			self.logger.debug("Connected to database %s" % self.db_name)

			self.db_connection.isolation_level = 'EXCLUSIVE'
			self.db_connection.execute('BEGIN EXCLUSIVE')

		except sqlite3.Error as e:
			self.logger.error("%s" % e.args[0])
			
	def get_database_cursor(self):
		try:
			self.db_cursor = self.db_connection.cursor()
			self.logger.debug("Obtained database cursor to %s" % self.db_name)
		except sqlite3.Error as e:
			self.logger.error("%s" % e.args[0])

	def create_table(self, field_names):
		try:
			self.db_cursor.execute('''CREATE TABLE %s (%s);''' % (self.table_name, field_names))
			self.logger.debug("Created table %s" % self.table_name)
		except sqlite3.Error as e:
			self.logger.error("%s" % e.args[0])

	def insert_two_to_table(self, values):
		for x in range(0,30):
			try:
				with self.db_connection: 
					self.db_cursor.execute('''INSERT INTO %s VALUES (?,?);''' % self.table_name, (values))
					self.logger.debug("Inserted %s to %s" % (values, self.table_name))
			except:
				time.sleep(1)
				pass
			finally:
				break
		else:
			with self.db_connection:
				try:
					self.db_cursor.execute('''INSERT INTO %s VALUES (?,?);''' % self.table_name, (values))
					self.logger.debug("Inserted %s to %s" % (values, self.table_name))
				except sqlite3.Error as e:
					self.logger.error("%s" % e.args[0])

	def insert_three_to_table(self, values):
		for x in range(0,30):
			try:
				with self.db_connection: 
					self.db_cursor.execute('''INSERT INTO %s VALUES (?,?,?);''' % self.table_name, (values))
					self.logger.debug("Inserted %s to %s" % (values, self.table_name))
			except:
				time.sleep(1)
				pass
			finally:
				break
		else:
			with self.db_connection:
				try:
					self.db_cursor.execute('''INSERT INTO %s VALUES (?,?,?);''' % self.table_name, (values))
					self.logger.debug("Inserted %s to %s" % (values, self.table_name))
				except sqlite3.Error as e:
					self.logger.error("%s" % e.args[0])

	def insert_four_to_table(self, values):
		for x in range(0,30):
			try:
				with self.db_connection: 
					self.db_cursor.execute('''INSERT INTO %s VALUES (?,?,?,?);''' % self.table_name, (values))
					self.logger.debug("Inserted %s to %s" % (values, self.table_name))
			except:
				time.sleep(1)
				pass
			finally:
				break
		else:
			with self.db_connection:
				try:
					self.db_cursor.execute('''INSERT INTO %s VALUES (?,?,?,?);''' % self.table_name, (values))
					self.logger.debug("Inserted %s to %s" % (values, self.table_name))
				except sqlite3.Error as e:
					self.logger.error("%s" % e.args[0])

	def simple_select_from_database(self, field, key, key_value):
		self.logger.debug("SELECT %s FROM %s WHERE %s=%s;" % (field, self.table_name, key, key_value))
		for x in range(0,30):
			try:
				with self.db_connection: 
					self.db_cursor = self.db_cursor.execute('''SELECT %s FROM %s WHERE %s=?;''' % (field, self.table_name, key), [key_value])
			except:
				time.sleep(1)
				pass
			finally:
				break
		else:
			with self.db_connection:
				try:
					self.db_cursor = self.db_cursor.execute('''SELECT %s FROM %s WHERE %s=?;''' % (field, self.table_name, key), [key_value])
				except sqlite3.Error as e:
					self.logger.error("%s" % e.args[0])

		#return self.db_cursor.fetchall()
		#return self.db_cursor.fetchone()

	def simple_delete_from_database(self, key, key_value):
		for x in range(0,30):
			try:
				with self.db_connection: 
					self.logger.debug("DELETE FROM %s WHERE %s=%s;" % (self.table_name, key, key_value))
					self.db_cursor.execute("DELETE FROM %s WHERE %s=%s;" % (self.table_name, key, key_value))
					self.logger.debug("Deleted row where %s contained value of %s from %s" % (key, key_value, self.table_name))
			except:
				time.sleep(1)
				pass
			finally:
				break
		else:
			with self.db_connection:
				try:
					self.logger.debug("DELETE FROM %s WHERE %s=%s;" % (self.table_name, key, key_value))
					self.db_cursor.execute("DELETE FROM %s WHERE %s=%s;" % (self.table_name, key, key_value))
					self.logger.debug("Deleted row where %s contained value of %s from %s" % (key, key_value, self.table_name))
				except sqlite3.Error as e:
					self.logger.error("%s" % e.args[0])

	def commit_changes(self):
		try:
			self.db_connection.commit()
			self.logger.debug("Committed %s total changes to table %s in %s" % (self.db_connection.total_changes, self.table_name, self.db_name))
		except sqlite3.Error as e:
			self.logger.error("%s" % e.args[0])

	def close_connection(self):
		try:
			self.db_connection.close()
			self.logger.debug("Closed connection to %s" % self.db_name)
		except sqlite3.Error as e:
			self.logger.error("%s" % e.args[0])
