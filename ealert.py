#! python
#! -*- coding: utf-8 -*-

"""
Ealert class to interface with Derdack Enterprise Alert.

Tested with Derdack Enterprise Alert 2015
Tested with Python 3.4.3
"""

import base64
from logger import Logger
import os
from suds.client import Client
import sys

__author__ = "Dan Newburg"
__version__ = "1.0.1"
__maintainer__ = "Dan Newburg"
__email__ = "dan.newburg@gmail.com"
__status__ = "Development"

class EAlertConnection():
	def __init__(self, debug, log_path, username, password, uri, provider):
		self.client = None
		self.event_array = None
		self.logger = Logger(self.__class__.__name__, debug, log_path).get_logger()
		self.password = password
		self.provider = provider
		self.uri = uri		
		self.username = username
		self.result = None
		
	def set_client(self):
		self.client = Client(self.uri)

	def set_event_array(self):
		self.event_array = self.client.factory.create('ArrayOfEventParameter')

	def append_event_parameter(self, name, value):
		parameter = self.client.factory.create('EventParameter')
		parameter.Name = "%s" % name
		parameter.Value = "%s" % value
		self.event_array.EventParameter.append(parameter)

	def raise_event(self):
		try:
			self.result = self.client.service.RaiseEvent(Username=self.username,Password=self.password,ProviderName=self.provider,EventParameters=self.event_array)
			self.logger.info("[%s] Raised Event ID %s" % (os.getpid(), self.result))

		except Exception as detail:
			self.logger.error(detail)
			sys.exit(1)

	def reset_event(self,eventid,metric_name,metric_value,affected_fqdn, status):
		try:
			desc = "The %s alert for %s is now classified as a %s state with a value of %s." % (metric_name,affected_fqdn,status,metric_value)
			self.client.service.ResetEvent(Username=self.username,Password=self.password,ProviderName=self.provider,EventID=eventid,Description=desc)
			self.logger.info("[%s] Reset Event ID %s" % (os.getpid(), eventid))

		except Exception as detail:
			self.logger.error(detail)
			sys.exit(1)


