#! python
#! -*- coding: utf-8 -*-

"""
Logger class to initialize logging for classes.
"""

__author__ = "Dan Newburg"
__version__ = "1.0.0"
__maintainer__ = "Dan Newburg"
__email__ = "dan.newburg@gmail.com"
__status__ = "Development"

import os
import logging

class Logger:
	def __init__(self, name, debug, path):
		name = name.replace('.log','')
		logger = logging.getLogger(name)
		if debug:
			logger.setLevel(logging.DEBUG)
		else:
			logger.setLevel(logging.INFO)

		if not logger.handlers:
			handler = logging.FileHandler(path)
			formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] [%(name)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %Z')
			handler.setFormatter(formatter)
			if debug:
				handler.setLevel(logging.DEBUG)
			else:
				handler.setLevel(logging.INFO)
			logger.addHandler(handler)
			self._logger = logger

	def get_logger(self):
		return self._logger
