import appdaemon.plugins.hass.hassapi as hass
import datetime
import re
import mqttapi as mqtt

class DoorAlarmApp(hass.Hass):

	def initialize(self):

		self.doorState = self.get_state(entity_id = self.args['door'])
		self.timeout = self.args['timeout']
		self.lastNotificationSent = datetime.datetime.now()
		self.minsBetweenNotifications = 5

		# Contains the reference to the notifyAlarm_callback, if any.
		self.timer = None

		self.listen_state(self.doorClosed_callback)
		self.listen_state(self.doorOpen_callback)

		# Set the callbacks based on the inital state of the door.
		if (self.doorState == 'on'):
			self.timer = self.run_in(self.notifyAlarm_callback, self.timeout)


	def doorClosed_callback(self, entity, attribute, old, new, kwargs):
		self.cancel_timer(self.timer)


	def doorOpen_callback(self, entity, attribute, old, new, kwargs):
		self.timer = self.run_in(self.notifyAlarm_callback, self.timeout)


	def notifyAlarm_callback(self, kwargs):
		self.call_service("notify/petes_ios_devices", title = "Door Alert!", message = ("A door has been left open for " + str(self.timeout) + "minutes."))
		self.lastNotificationSent = datetime.datetime.now()
		self.timer = self.run_in(self.notifyAlarm_callback, self.timeout)