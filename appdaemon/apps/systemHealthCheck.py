from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from icmplib import ping
from jinja2 import Environment, FileSystemLoader

import appdaemon.plugins.hass.hassapi as hass
import datetime
import os
import pytest
import re
import smtplib, ssl
import subprocess
import time
import yaml

class SystemHealthCheckApp(hass.Hass):

	# Tests
	def ensureKasaSwitchEntitiesAvailable(self):
		self.kasa_entities = ['switch.bedroom_reading_lamp', 'switch.kitchen_lighting_strip']
		for entity in self.kasa_entities:
			if (self.get_state(entity_id = str(entity), attribute = 'state') == 'unavailable'):
				return -1
		return 0

	def checkHueMotionSensorsOK(self):
		# Entities available?
		self.hue_motion_sensor_entities = ['binary_sensor.entrance_foyer_sensor_motion', 'binary_sensor.evies_bedroom_sensor_motion', 'binary_sensor.hallway_downstairs_sensor_motion', 'binary_sensor.storeroom_sensor_motion', 'binary_sensor.toilet_sensor_motion']
		for self.entity in self.hue_motion_sensor_entities:
			if (self.get_state(entity_id = str(self.entity), attribute = 'state') == 'unavailable'):
				return -1
		# Battery levels > 20%?
		# TODO - FIX
		#for self.entity in self.hue_motion_sensor_entities:
			#if (self.get_state(entity_id = str(self.entity), attribute = 'battery_level') <= 20):
				#return -1
		return 0

	def ensureNestProtectEntitiesAvailable(self):
		# Entities available?
		self.hue_nest_protect_entities = ['sensor.entrance_foyer_nest_protect_color_status', 'sensor.upstairs_nest_protect_color_status']
		for self.entity in self.hue_nest_protect_entities:
			if (self.get_state(entity_id = str(self.entity), attribute = 'state') != 'green'):
				return -1
		return 0

	def ensurePrinterEntityAvilable(self):
		if (self.get_state(entity_id = 'sensor.samsung_m283x_series', attribute = 'state') == 'unavailable'):
			return -1
		return 0	

	# TODO: would be great to parameterize this, and also to check that the MAC addr is corect.
	def ensurePingGateway(self, ipAddr):
		host = ping(ipAddr, count = 10, interval = 0.2)
		if (host.is_alive == False):
			return -1
		return 0

	def ensureResolveDomainName(self, dnsServer):
		result = (subprocess.run(["nslookup", "google.com", dnsServer], stdout = subprocess.PIPE)).stdout
		if (re.search(b"server can\'t find", result) != None):
		    return -1
		return 0

	def ensureSpeedTestOK(self):
		# Do I have a recent speed test? (I.e. < 5 hours old)
		timeLastTest = datetime.datetime.strptime(self.get_state(entity_id = "sensor.speedtest_download", attribute = "last_updated"), "%Y-%m-%dT%H:%M:%S.%f%z")
		if ((datetime.datetime.now(datetime.timezone.utc) - timeLastTest).seconds > 5 * 3600):
			return -1

		# Is the result acceptable? (I.e. downlink >= 40 Mbps, uplink >= 15 Mbps, ping < 40ms)
		downlink = float(self.get_state(entity_id = "sensor.speedtest_download", attribute = 'state'))
		uplink = float(self.get_state(entity_id = "sensor.speedtest_upload", attribute = 'state'))
		ping = float(self.get_state(entity_id = "sensor.speedtest_ping", attribute = 'state'))
		if ((downlink < 40) or (uplink < 15) or (ping > 40)):
			return -1

		return 0

	def ensurePiPerformanceOK(self):
		# Do I have recent information? (I.e. < 30 mins ago)
		timeLastTest = datetime.datetime.strptime(self.get_state(entity_id = "sensor.processor_use", attribute = "last_updated"), "%Y-%m-%dT%H:%M:%S.%f%z")
		if ((datetime.datetime.now(datetime.timezone.utc) - timeLastTest).seconds > 1800):
			return -1

		# Is the result acceptable?
		cpu = float(self.get_state(entity_id = "sensor.processor_use", attribute = 'state'))
		disk = float(self.get_state(entity_id = "sensor.disk_use_percent", attribute = 'state'))
		memory = float(self.get_state(entity_id = "sensor.memory_use_percent", attribute = 'state'))
		swap = float(self.get_state(entity_id = "sensor.swap_use_percent", attribute = 'state'))
		if ((cpu > 95) or (disk > 90) or (memory > 95) or (swap > 95)):
			return -1

		return 0

	def ensureAllBatteryPoweredDevicesOK(self):
		acceptableThreshold = 20

		# TODO: Get whole entity structure, remove all items that have no attribute 'battery'
		# TODO: Iterate dict. If any element contains attribute 'battery' < self.acceptableThreshold, return -1
		allHAEntities = self.get_state()
		self.log(allHAEntities)


		return 0


 	# Primitives

	# AppDaemon Core Functions
	def initialize(self):
		startTime = datetime.time(6, 0, 0)
		self.run_daily(self.dailySystemHealthCheck, startTime, emailReport = True)
		self.run_daily(self.dailySystemHealthCheck, datetime.time(13, 56, 0), emailReport = True)

	def dailySystemHealthCheck(self, kwargs):
		self.log("Daily system health check - commenced.")
		
		results = []

		# Entity checks
		results.append(["TC01: Are the Kasa entities Available?", self.ensureKasaSwitchEntitiesAvailable()])
		results.append(["TC02: Are the Hue Motion Sensors ok?", self.checkHueMotionSensorsOK()])
		results.append(["TC03: Are the Nest Protect Sensors ok?", self.ensureNestProtectEntitiesAvailable()])
		results.append(["TC04: Is the printer ok?", self.ensurePrinterEntityAvilable()])
		
	  	# Internal network checks
		results.append(["TC05: Can I ping the gateway (192.168.0.1)?", self.ensurePingGateway("192.168.0.1")])
		results.append(["TC06: Can I DNS-resolve google.com (via Google - 8.8.8.8)?", self.ensureResolveDomainName("8.8.8.8")])
		results.append(["TC07: Can I DNS-resolve google.com (via PiHole - 192.168.0.46)?", self.ensureResolveDomainName("192.168.0.46")])
		results.append(["TC08: Do I have a recent, good speed-test?", self.ensureSpeedTestOK()])
		results.append(["TC09: Is the Raspberry Pi operating nominally?", self.ensurePiPerformanceOK()])

		# Other, not easily categorised stuff.
		results.append(["TC10: Are my battery-powered devices sufficiently charged?", self.ensureAllBatteryPoweredDevicesOK()])

		# TODO items
#		results.append(["TCxx: Can I see and connect to WiFi (SSID: YoP)?", str()])
#		results.append(["TCxx: Can I see the NAS, and access its public share?", str()])
#		results.append(["TCxx: Can I see the three Sonos players?", str()])
#		results.append(["TCxx: Can I see any rogue / unexpected devices on my network?", str()])

		# Additional Tests that would be great - given Fing.
		#
		# TODO: would be great to verify operation of a single DHCP server at 192.168.0.46, and nowhere else, esp .1
		# TODO: would be great to verify that that DHCP server gives out ADDrs on the 200-250 range, with the right subnet mark, range. Poss as part of WiFI test.
		# TODO: confirm network time.
		# TODO: confirm list of common URLs are browseable.
		# TODO: confirm external IP, and that it falls within a block you'd expect to see (not sure how to do).

		self.log("Daily system health check - completed.")

		if (kwargs['emailReport'] == True):
			with open("/config/secrets.yaml", "r") as f:
				try:
					yamlData = yaml.safe_load(f)
				except Exception:
					self.log("Error: unable to parse yaml secrets file.")
		    
			emailReceiverAddr = yamlData['gmail']['receiverAddr']
			emailSenderAddr = yamlData['gmail']['senderAddr']
			emailPassword = yamlData['gmail']['password']

			context = ssl.create_default_context()

			now = datetime.datetime.now()
			message = MIMEMultipart()
			message['Subject'] = "Daily System Health Check completed " + now.strftime("%B %d, %Y at %H:%M:%S")
			message['From'] = "lists@peterwills.com"
			message['To'] = "peter@peterwills.com"
			
			body = ""
			for line in results:
				if (line[1] == 0):
					color = "green"
				else:
					color = "red"
				body += ("<p style = \"color:" + color + "\">" + str(line[0]) + ": " + str(line[1]) + "</p>\n")

			message.attach(MIMEText(body, "html"))

			try:
				server = smtplib.SMTP("smtp.gmail.com", 587)
				server.ehlo() # Can be omitted
				server.starttls(context = context) # Secure the connection
				server.ehlo() # Can be omitted
				server.login(emailSenderAddr, emailPassword)
				server.sendmail("lists@peterwills.com", "peter@peterwills.com", message.as_string())  
				server.quit()
				self.log("Successfully sent email")
			except Exception:
				self.log("Error: unable to send email")

# PyTest tests
def testAlwaysPasses():
	return True


