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
		self.listen_state(self.onPetesPhoneWiFiChange_callback, "sensor.steve_jobs_iphone_3g_ssid")

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


	def onPetesPhoneWiFiChange_callback(self, entity, attribute, old, new, kwargs):
		# I'm going to experiment with setting my occupancy state based on the App's reporting of which WiFi SSID I'm on.
		# Credit for the suggestion: https://hasspodcast.io/ha076/
		if (new == "YoP"):
			# It seems to lose the attributes if I set the state on its own. So, experimenting with being explicit on the attribs as well.
			self.set_state("person.pete", state = "home", attributes = {"name": "Pete", "id": "9171f88c29f143e9a2a2f5ea2890339d"})
		elif(new == "Not Connected"):
			self.set_state("person.pete", state = "not_home", attributes = {"name": "Pete", "id": "9171f88c29f143e9a2a2f5ea2890339d"})
