#!/usr/bin/env python
#-*- coding: UTF-8 -*-

# autor: Ignacio Gilbaja
# date: 2013-05-06
# version: 1.1

##################################################################################
# version 1.0 release notes: extract data from MySQL and generate json
# Initial version
# Requisites: library python-mysqldb. To install: "apt-get install python-mysqldb"
##################################################################################


import MySQLdb
import logging, logging.handlers
import os
import time
import json

#### VARIABLES #########################################################
from configobj import ConfigObj
config = ConfigObj('./visor.properties')

INTERNAL_LOG_FILE = config['directory_logs'] + "/visor.log"
LOG_FOR_ROTATE = 10

MYSQL_IP = config['mysql_host']
MYSQL_PORT = config['mysql_port']
MYSQL_USER = config['mysql_user']
MYSQL_NAME = config['mysql_db_name']
MYSQL_PASSWORD = config['mysql_passwd']

INTERNAL_LOG = "/tmp/kyros-json.log"

########################################################################
# definimos los logs internos que usaremos para comprobar errores
log_folder = os.path.dirname(INTERNAL_LOG)

if not os.path.exists(log_folder):
	os.makedirs(log_folder)

try:
	logger = logging.getLogger('kyros-json')
	loggerHandler = logging.handlers.TimedRotatingFileHandler(INTERNAL_LOG , 'midnight', 1, backupCount=10)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	loggerHandler.setFormatter(formatter)
	logger.addHandler(loggerHandler)
	logger.setLevel(logging.DEBUG)
except:
	print '------------------------------------------------------------------'
	print '[ERROR] Error writing log at %s' % INTERNAL_LOG
	print '[ERROR] Please verify path folder exits and write permissions'
	print '------------------------------------------------------------------'
	exit()
########################################################################


def getTracking():
	try:
		dbKyros4 = MySQLdb.connect(MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)
	except:
		logger.error('Error connecting to database: IP:%s, USER:%s, PASSWORD:%s, DB:%s', MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)

	cursor = dbKyros4.cursor()
	cursor.execute("""SELECT DEVICE_ID as DEV, POS_LATITUDE_DEGREE + POS_LATITUDE_MIN/60 as LAT, POS_LONGITUDE_DEGREE + POS_LONGITUDE_MIN/60 as LON, HEADING AS HEAD from TRACKING_1""" )
	result = cursor.fetchall()
	
	try:
		return result
	except Exception, error:
		logger.error('Error getting data from database: %s.', error )
		
	cursor.close
	dbFrontend.close

while True:
	array_list = []
	trackingInfo = getTracking()

	for tracking in trackingInfo:
		position = {"geometry": {"type": "Point", "coordinates": [tracking[2], tracking[1]]}, "type": "Feature", "properties":{"name":str(tracking[0]), "heading":tracking[3]}}
		array_list.append(position)

	with open('/var/www/tracking.json', 'w') as outfile:
		json.dump(array_list, outfile)
	
	time.sleep(2)
