#! python
#! -*- coding: utf-8 -*-

"""
Wily EAlert integrates CA Application Performance Management (Wily) with Derdack Enterprise Alert.
The tool offers event status management (open and closed state of an event) and field normalization.

Tested with Python 3.4.3.
"""

__author__ = "Dan Newburg"
__version__ = "1.1.5"
__maintainer__ = "Dan Newburg"
__email__ = "dan.newburg@frostbank.com / dan.newburg@gmail.com"
__status__ = "Development"

import base64
import configparser
from database import Database
import datetime
import ealert
from logger import Logger
from optparse import OptionParser
import os
import re
import socket
from socket import error as socket_error
import sys
import time

def init_parser():
	parser = OptionParser()
	parser.add_option("-1", "--alert_teams", action="store", type="string", dest="alert_teams")
	parser.add_option("-2", "--alert_text", action="store", type="string", dest="alert_text")
	parser.add_option("-3", "--alert_name", action="store", type="string", dest="alert_name")
	parser.add_option("-4", "--alert_status", action="store", type="string", dest="alert_status")	
	parser.add_option("-5", "--time", action="store", type="string", dest="event_time")		
	parser.add_option("-6", "--metric_name", action="store", type="string", dest="metric_name")		
	parser.add_option("-7", "--threshold", action="store", type="string", dest="threshold")	

	return parser

def parse_arguments(logger, parser):
	(options, args) = parser.parse_args(sys.argv)
	logger.debug("Preparing alert attribute alert_teams with value: %s." % options.alert_teams)
	logger.debug("Preparing alert attribute alert_name with value: %s." % options.alert_text)
	logger.debug("Preparing alert attribute alert_name with value: %s." % options.alert_name)
	logger.debug("Preparing alert attribute alert_status with value: %s." % options.alert_status)
	logger.debug("Preparing alert attribute event_time with value: %s." % options.event_time)
	logger.debug("Preparing alert attribute metric_name with value: %s." % options.metric_name)
	logger.debug("Preparing alert attribute threshold with value: %s." % options.threshold)

	return options

def parse_metric_value(logger, string):
	regex = re.compile(".*\s=\s(\d+)")
	try:
		value = regex.match(string).group(1)
		logger.debug("Parsed metric value: %s" % value)
	except AttributeError as detail:
		value = "N/A"
		logger.error("Unable to parse metric value from string.\n%s" % detail)

	return value

def parse_teams(teams):
	return teams.split(',')

def parse_metric_string_components(metric_name):
	return metric_name.split('|')

def get_ip_addr(logger, host):
	logger.debug("Will query DNS for host %s" % host)

	try:
		ip_addr = socket.gethostbyname("%s" % host)
		logger.debug("DNS returned %s for %s" % (ip_addr,host))
	except socket_error:
		try:
			ip_addr = socket.gethostbyname("%s.dmz.local" % host)
			logger.debug("DNS returned %s for %s" % (ip_addr,host))
		except socket_error:
			ip_addr = "None"
			logger.debug("No IP address available for host %s" % host)

	return ip_addr

def get_fqdn(logger, host):
	logger.debug("Will query DNS for host %s" % host)
	try:
		fqdn = socket.gethostbyaddr("%s" % host)
		logger.debug("DNS returned %s for %s" % (fqdn,host))
	except socket_error:
		fqdn = "None"
		logger.debug("No hostname available for host %s" % host)

	return fqdn[0]

def get_hostname():
	return socket.gethostname()

def normalize_status(logger, status):
	logger.debug("Normalizing status with value of %s" % status)
	if status == "2":
		logger.debug("Status normalized to 'Major'.")
		return "Major"
	if status == "3":
		logger.debug("Status normalized to 'Critical'.")
		return "Critical"
	logger.debug("Status normalized to 'Low'.")

	return "Low"
	
def main():
	today = datetime.date.today()
	parser = init_parser()
	config = configparser.ConfigParser()
	config.read('wily_ealert.ini')

	logging_path = os.path.join(config['logging']['logdir'],'ealert_%s%s%s.log' % (today.month,today.day,today.year))
	logger = Logger("Wily EAlert", config['logging']['debug'], logging_path).get_logger()
	options = parse_arguments(logger, parser)

	affected_ip_addr = "None"
	affected_fqdn = "None"
	metric_string_components = parse_metric_string_components(options.metric_name)
	for metric_string_component in metric_string_components:
		if get_ip_addr(logger, metric_string_component) != "None":
			affected_ip_addr = get_ip_addr(logger, metric_string_component)
			affected_fqdn = get_fqdn(logger, affected_ip_addr)

	affected_metric_value = parse_metric_value(logger, options.alert_text)
	status = normalize_status(logger, options.alert_status)
	monitoring_host = get_hostname()
	monitoring_ip_addr = get_ip_addr(logger, monitoring_host)
	monitoring_fqdn = get_fqdn(logger, monitoring_ip_addr)
	monitoring_source = "Wily"
	team_list = parse_teams(options.alert_teams)

	ealert_db_path = os.path.join(config['ealert']['datadir'],'events.db')
	ealert_db_path_ok = os.path.exists(ealert_db_path)

	if ealert_db_path_ok == False:
		logger.info("%s does not exist. Database will be created." % ealert_db_path)

	ealert_db = Database(ealert_db_path, "event_table", config['logging']['debug'], logging_path)
	ealert_db.connect_to_database()
	ealert_db.get_database_cursor()

	if ealert_db_path_ok == False:
		event_table_fields = "fqdn TEXT, metricname TEXT, eventtime TEXT, eventid TEXT"
		ealert_db.create_table(event_table_fields)

	ealert_connection = ealert.EAlertConnection(config['logging']['debug'], logging_path, config['ealert']['username'], \
	 base64.b64decode(str.encode(config['ealert']['password'])).decode('utf-8'), config['ealert']['uri'], config['ealert']['provider'])
	ealert_connection.set_client()

	if options.alert_status != "3":
		ealert_db.simple_select_from_database("eventid", "metricname", options.metric_name)
		event_ids = list(set(ealert_db.db_cursor.fetchall()))
		logger.debug("IDs: %s" % event_ids)
		if len(event_ids) > 0:
			while event_ids:
				event_id = event_ids.pop()[0]
				ealert_connection.reset_event(event_id,options.metric_name,affected_metric_value,affected_fqdn,status)
				ealert_db.simple_delete_from_database("eventid", event_id)
				ealert_db.commit_changes()
		else:
			logger.debug("No events found to close for metric name %s." % options.metric_name)

	if options.alert_status != "1":
		escalation_team = None
		broadcast_team = None
		if options.alert_status == "3":
			escalation_team = team_list.pop(0)
		if len(team_list) > 0:
			broadcast_team = ",".join(map(str,team_list))
		
		ealert_connection.set_event_array()
		ealert_connection.append_event_parameter("alertname",options.alert_name)
		ealert_connection.append_event_parameter("alertstatus",status)
		ealert_connection.append_event_parameter("eventtime",options.event_time)
		ealert_connection.append_event_parameter("metricname",options.metric_name)
		ealert_connection.append_event_parameter("threshold",options.threshold)
		ealert_connection.append_event_parameter("metricvalue",affected_metric_value)
		ealert_connection.append_event_parameter("ipaddr",affected_ip_addr)
		ealert_connection.append_event_parameter("fqdn",affected_fqdn)
		ealert_connection.append_event_parameter("monitoringfqdn",monitoring_fqdn)
		ealert_connection.append_event_parameter("monitoringipaddr",monitoring_ip_addr)
		ealert_connection.append_event_parameter("monitoringsource",monitoring_source)
		ealert_connection.append_event_parameter("escalationteam",escalation_team)
		ealert_connection.append_event_parameter("broadcastteams",broadcast_team)
		ealert_connection.raise_event()
		values = affected_fqdn, options.metric_name, options.event_time, ealert_connection.result
		ealert_db.insert_four_to_table(values)
		ealert_db.commit_changes()

	ealert_db.close_connection()
	
if __name__ == "__main__":
	main()
