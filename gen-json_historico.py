#!/usr/bin/env python
#-*- coding: UTF-8 -*-

# autor: Carlos Rueda
# date: 2015-07-01
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
#config = ConfigObj('/opt/gen-json/visor_wrc.properties')
config = ConfigObj('./visor_wrc.properties')

INTERNAL_LOG_FILE = config['directory_logs'] + "/visor_wrc.log"
LOG_FOR_ROTATE = 10

MYSQL_IP = config['mysql_host']
MYSQL_PORT = config['mysql_port']
MYSQL_USER = config['mysql_user']
MYSQL_NAME = config['mysql_db_name']
MYSQL_PASSWORD = config['mysql_passwd']

INTERNAL_LOG = "/tmp/kyros-json.log"

PID = "/var/run/json-generator"


########################################################################
# definimos los logs internos que usaremos para comprobar errores
log_folder = os.path.dirname(INTERNAL_LOG)

if not os.path.exists(log_folder):
	os.makedirs(log_folder)

try:
	logger = logging.getLogger('wrc-json')
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


def getTrackingHistorico():
	#dbKyros4 = MySQLdb.connect(MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)
	try:
		dbKyros4 = MySQLdb.connect(MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)
	except:
		logger.error('Error connecting to database: IP:%s, USER:%s, PASSWORD:%s, DB:%s', MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)

	cursor = dbKyros4.cursor()
	cursor.execute("""SELECT VEHICLE_LICENSE as DEV, POS_LATITUDE_DEGREE + POS_LATITUDE_MIN/60 as LAT, POS_LONGITUDE_DEGREE + POS_LONGITUDE_MIN/60 as LON, VEHICLE.START_STATE as STATUS from TRACKING where VEHICLE_LICENSE in ('001', '002', '003')""" )
	result = cursor.fetchall()
	
	try:
		return result
	except Exception, error:
		logger.error('Error getting data from database: %s.', error )
		
	cursor.close
	dbFrontend.close


def main():
	
	array_list = []
	trackingInfo = getTrackingHistorico()

	for tracking in trackingInfo:
		position = {"geometry": {"type": "Point", "coordinates": [tracking[2], tracking[1]]}, "type": "Feature", "properties":{"name":str(tracking[0]), "state":str(tracking[3])}}
		array_list.append(position)

	#with open('/var/www2/tracking_wrc.json', 'w') as outfile:
	with open('/Applications/MAMP/htdocs/visorKyros/tracking_historico.json', 'w') as outfile:
		json.dump(array_list, outfile)

	sys.exit()
 
if __name__ == '__main__':
    main()

