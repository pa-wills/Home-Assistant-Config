import appdaemon.plugins.hass.hassapi as hass
import datetime
import re
import mqttapi as mqtt


class PresenceOccupancyApp(hass.Hass):

	def initialize(self):
		self.AlarmNotifier_handler = None
		self.lastNotificationSent = datetime.datetime.now()
		self.minsBetweenNotifications = 5

		self.listen_state(self.becameOccupied_callback, "sensor.someone_home", new = "Occupied")
		self.listen_state(self.becameUnoccupied_callback, "sensor.someone_home", new = "Unoccupied")

	def becameOccupied_callback(self, entity, attribute, old, new, kwargs):
		# Turn up the sensitivities on Motion Sensors in the common areas.
		self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.entranceFoyer/set", payload = "{\"motion_sensitivity\": \"high\"}")
		self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.eviesBedroom/set", payload = "{\"motion_sensitivity\": \"high\"}")
		self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.hallwayDownstairs/set", payload = "{\"motion_sensitivity\": \"high\"}")
		self.call_service("mqtt/publish", topic = "zigbee2mqtt/motion.toilet/set", payload = "{\"motion_sensitivity\": \"high\"}")

		self.cancel_listen_state(self.AlarmNotifier_handler)


	def becameUnoccupied_callback(self, entity, attribute, old, new, kwargs):
		# Turn down the sensitivities on Motion Sensors in the common areas.
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

