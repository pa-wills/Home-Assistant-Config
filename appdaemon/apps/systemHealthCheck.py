from icmplib import ping

import appdaemon.plugins.hass.hassapi as hass
import datetime
import nslookup
import pytest
import time


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
		for self.entity in self.hue_motion_sensor_entities:
			if (self.get_state(entity_id = str(self.entity), attribute = 'battery_level') <= 20):
				return -1
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

	def ensurePingGateway(self):
		host = ping('192.168.0.1', count = 10, interval = 0.2)
		if (host.is_alive == False):
			return -1
		return 0

	def ensureResolveDomainName(self):
		# TODO: this needs signficant repair work.
		# I need to be able to deduce the difference between good/bad, and return the appropriate result.
		dns_query = Nslookup(dns_servers = ["8.8.8.8"])
		ips_record = dns_query.dns_lookup("www.google.hvdkh")
		self.log(str(ips_record.response_full) + " - " + str(ips_record.answer))
		return 0

	def ensureSpeedTestOK(self):
		# TODO: Do I have a recent speed test? (I.e. < 5 hours old)
		# TODO: Is the result acceptable? (I.e. downlink >= 40 Mbps, uplink >= 15 Mbps, ping < 40ms)
		return 0

 	# Primitives

	# AppDaemon Core Functions
	def initialize(self):
		startTime = datetime.time(6, 0, 0)
		self.run_daily(self.dailySystemHealthCheck, startTime)

	def dailySystemHealthCheck(self, kwargs):
		self.log("Daily system health check - commenced.")

		# Entity checks
		self.log("TC01: Are the Kasa entities Available? " + str(self.ensureKasaSwitchEntitiesAvailable()))
		self.log("TC02: Are the Hue Motion Sensors ok? " + str(self.checkHueMotionSensorsOK()))
		self.log("TC03: Are the Nest Protect Sensors ok? " + str(self.ensureNestProtectEntitiesAvailable()))
		self.log("TC04: Is the printer ok? " + str(self.ensurePrinterEntityAvilable()))

	  	# Network checks

		self.log("TCxx: Can I ping the gateway (192.168.0.1)? " + str(self.ensurePingGateway()))
		self.log("TCxx: Can I DNS-resolve google.com? " + str(self.ensureResolveDomainName()))
		self.log("TCxx: Do I have a recent, good speed-test? " + str(self.ensureSpeedTestOK()))
	#	self.log("TCxx: Can I see and connect to WiFi (SSID: YoP)? " + str())
	#	self.log("TCxx: Can I see any rogue / unexpected deviceson my network? " + str())
	#	self.log("" + str())

		# TODO: compile and email the result.
		# TODO: reflect the most recent state into a sensor.

		self.log("Daily system health check - completed.")



# PyTest tests
def testAlwaysPasses():
	return True


