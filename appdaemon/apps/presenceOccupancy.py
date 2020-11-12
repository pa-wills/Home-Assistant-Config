import appdaemon.plugins.hass.hassapi as hass
import datetime
import re
import mqttapi as mqtt


class PresenceOccupancyApp(hass.Hass):

	def initialize(self):
		self.listen_state(self.becameOccupied_callback, "sensor.someone_home", new = "Occupied")
		self.listen_state(self.becameUnoccupied_callback, "sensor.someone_home", new = "Unoccupied")

	def becameOccupied_callback(self, kwargs):
		# Turn up the sensitivities on Motion Sensors in the common areas.
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.entranceFoyer/set", payload = "{\"motion_sensitivity\": \"high\"}")
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.eviesBedroom/set", payload = "{\"motion_sensitivity\": \"high\"}")
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.hallwayDownstairs/set", payload = "{\"motion_sensitivity\": \"high\"}")
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.toilet/set", payload = "{\"motion_sensitivity\": \"high\"}")

	def becameUnoccupied_callback(self, kwargs):
		# Turn down the sensitivities on Motion Sensors in the common areas.
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.entranceFoyer/set", payload = "{\"motion_sensitivity\": \"low\"}")
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.eviesBedroom/set", payload = "{\"motion_sensitivity\": \"low\"}")
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.hallwayDownstairs/set", payload = "{\"motion_sensitivity\": \"low\"}")
		self.call_service("mqtt.publish", topic = "zigbee2mqtt/motion.toilet/set", payload = "{\"motion_sensitivity\": \"low\"}")
