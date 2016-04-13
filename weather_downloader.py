import ConfigParser
import csv
import datetime
import json
import logging
import os
import sys
from urllib2 import urlopen

def getUrl(farm):
	param_buffer = []
	for p in params:
		param_buffer.append('='.join([p, params[p]]))
	return '%s%f,%f?%s' % (base_url, farm['lat'], farm['lon'], '&'.join(param_buffer))

def loadConfigFile():

	try:
		config = ConfigParser.ConfigParser()
		config.read(config_file)
		global API_key
		API_key = config.get('API_key', 'API_key')
	except Exception as e:
		logging.exception(e)
		sys.exit(1)
	
def writeJsonToCSV(jsonObj, filePath):

	try:
		with open(filePath, 'wb') as csvfile:
			writer = csv.writer(csvfile)
			
			head = []
			for row in jsonObj:
				
				for attr in row:
					if attr not in head:
						head.append(attr)
			
			writer.writerow(head)
			
			writerBuffer = []
			for row in jsonObj:
				
				buffer = []
				for attr in head:
				
					if attr in row:
						buffer.append(row[attr])
					else:
						buffer.append('')
					
				writerBuffer.append(buffer)
				
			for row in writerBuffer:
				writer.writerow(row)
		
		logging.info(' '.join([filePath, ' - COMPLETED..']))
	
	except Exception as e:
		logging.exception(e)

		
def downloadWeatherJsonToCSV(url, filePath):

	try:
		response = json.loads(urlopen(url).read())
		writeJsonToCSV(response['hourly']['data'], filePath + '_hourly.csv')
		writeJsonToCSV(response['daily']['data'], filePath + '_daily.csv')
	
	except Exception as e:
		logging.exception(e)

# Init

FORMAT = "%(asctime)s - %(message)s"
logging.basicConfig(level=logging.INFO, filename='weather_downloader.log', format=FORMAT)

global API_key
config_file = 'config.cfg'
loadConfigFile()
base_url = 'https://api.forecast.io/forecast/%s/' % (API_key)
params = {'units': 'ca', 'exclude': 'currently,alerts,flags'}
ws_path = '%s/Weather_Data' % (os.getcwd())

# Main

with open('locations.json', 'rb') as locations_file:
	locations = json.loads(locations_file.read())

today_str = datetime.date.today().__str__()

for name in locations:
	
	farm = locations[name]
	url = getUrl(farm)
	path = '/'.join([ws_path, name])
	
	try:
		if not os.path.exists(path): os.makedirs(path)
		filePath = '/'.join([path, today_str])
		
		downloadWeatherJsonToCSV(url, filePath)
		
	except Exception as e:
		logging.exception(e)
