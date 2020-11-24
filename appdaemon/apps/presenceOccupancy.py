import appdaemon.plugins.hass.hassapi as hass
import datetime
import re
import mqttapi as mqtt


class PresenceOccupancyApp(hass.Hass):

	def initialize(self):

		# Variables for Evie's sleep alarm.
		self.AlarmNotifier_handler = None
		self.lastNotificationSent = datetime.datetime.now()
		self.minsBetweenNotifications = 5

		# Variables for the House Mode.
		self.timedNextStateTransition_handler = None

		# Actions in response to changes to the House Mode
		self.listen_state(self.OccupiedStateChange_callback, "sensor.someone_home")

		# Actions that give rise to Changes to the House Mode
		self.listen_state(self.onPersonStateChange_callback, "person")
		self.listen_state(self.onGuestModeStateChange_callback, "input_boolean.boolean_occupancy_guest_mode")


	# ** Functions that depend on, but do not set, the House Mode
	def OccupiedStateChange_callback(self, entity, attribute, old, new, kwargs):
		if (self.get_state("sensor.someone_home") == "Just Arrived"):
			# Turn up the sensitivities on Motion Sensors in the common areas, cancel the alarm.
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.entranceFoyer/set", payload = "{\"motion_sensitivity\": \"high\"}")
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.eviesBedroom/set", payload = "{\"motion_sensitivity\": \"high\"}")
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.hallwayDownstairs/set", payload = "{\"motion_sensitivity\": \"high\"}")
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.toilet/set", payload = "{\"motion_sensitivity\": \"high\"}")
			self.cancel_listen_state(self.AlarmNotifier_handler)

		elif (self.get_state("sensor.someone_home") == "Just Left"):
			# Turn down the sensitivities on Motion Sensors in the common areas, arm the alarm.
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.entranceFoyer/set", payload = "{\"motion_sensitivity\": \"low\"}")
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.eviesBedroom/set", payload = "{\"motion_sensitivity\": \"low\"}")
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.hallwayDownstairs/set", payload = "{\"motion_sensitivity\": \"low\"}")
			self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.toilet/set", payload = "{\"motion_sensitivity\": \"low\"}")
			self.AlarmNotifier_handler = self.listen_state(self.onMotion_callback, "group.sensors_motion_indoor_all", new = "on")

	def onMotion_callback(self, entity, attribute, old, new, kwargs):
		timeSinceLastNotification = ((datetime.datetime.now() - self.lastNotificationSent).seconds)
		if (timeSinceLastNotification >= (60 * self.minsBetweenNotifications)):
			self.call_service("notify/petes_ios_devices", title = "Security Alert!", message = "Motion detected despite nobody being home.")
			self.lastNotificationSent = datetime.datetime.now()


	# ** Implementation of the State Machine for House Mode **
	def onPersonStateChange_callback(self, entity, attribute, old, new, kwargs):
		# This is my implementation of Phil's state machine: https://philhawthorne.com/making-home-assistants-presence-detection-not-so-binary/
		# INVARIANT: this is one of the only parts of the code that writes to sensor.someone_home.
		if ((self.get_state("sensor.someone_home") == "Occupied") or (self.get_state("sensor.someone_home") == "Just Arrived")):
			if ((self.get_state("person.emma") == "not home") and (self.get_state("person.pete") == "not home") and (self.get_state("input_boolean.boolean_occupancy_guest_mode") == "false")):
				self.set_state("sensor.someone_home", state = "Just Left")
				if (self.timedNextStateTransition_handler != None):
					self.cancel_listen_state(self.timedNextStateTransition_handler)
				self.timedNextStateTransition_handler = self.run_in(self.onHouseModeNextStateTransition_callback, 1800, next_state = "Away")

		elif (self.get_state("sensor.someone_home") == "Just Left"):
			if ((self.get_state("person.emma") == "home") or (self.get_state("person.pete") == "home")):
				self.set_state("sensor.someone_home", state = "Home")
				if (self.timedNextStateTransition_handler != None):
					self.cancel_listen_state(self.timedNextStateTransition_handler)

		elif ((self.get_state("sensor.someone_home") == "Away") or (self.get_state("sensor.someone_home") == "Extended Away")):
			if ((self.get_state("person.emma") == "home") or (self.get_state("person.pete") == "home")):
				self.set_state("sensor.someone_home", state = "Just Arrived")
				if (self.timedNextStateTransition_handler != None):
					self.cancel_listen_state(self.timedNextStateTransition_handler)
				self.timedNextStateTransition_handler = self.run_in(self.onHouseModeNextStateTransition_callback, 1800, next_state = "Home")

	def onGuestModeStateChange_callback(self, entity, attribute, old, new, kwargs):
		# Update the House Mode based on the Guest Mode state-changes.
		# INVARIANT: this is one of the only parts of the code that writes to sensor.someone_home.
		if ((new == "on") and (self.get_state("sensor.someone_home") != "Occupied")):
			self.set_state("sensor.someone_home", state = "Occupied")
		elif ((new == "on") and (self.get_state("person.emma") == "not home") and (self.get_state("person.pete") == "not home")):
			self.set_state("sensor.someone_home", state = "Just Left")
			if (self.timedNextStateTransition_handler != None):
				self.cancel_listen_state(self.timedNextStateTransition_handler)
			self.timedNextStateTransition_handler = self.run_in(self.onHouseModeNextStateTransition_callback, 1800, next_state = "Away")

	def onHouseModeNextStateTransition_callback(self, kwargs):
		if (kwargs["next_state"] == "Away"):
			self.set_state("sensor.someone_home", state = "Away")
			if (self.timedNextStateTransition_handler != None):
				self.cancel_listen_state(self.timedNextStateTransition_handler)
			self.timedNextStateTransition_handler = self.run_at(self.onHouseModeNextStateTransition_callback, "sunrise", next_state = "Extended Away")
		elif (kwargs["next_state"] == "Extended Away"):
			self.set_state("sensor.someone_home", state = "Extended Away")
			if (self.timedNextStateTransition_handler != None):
				self.cancel_listen_state(self.timedNextStateTransition_handler)
		elif (kwargs["next_state"] == "Home"):
			self.set_state("sensor.someone_home", state = "Home")
			if (self.timedNextStateTransition_handler != None):
				self.cancel_listen_state(self.timedNextStateTransition_handler)



