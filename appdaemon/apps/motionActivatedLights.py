# Credit where it's due. Taken from:
# https://webworxshop.com/home-assistant-automation-in-depth-fusing-sensors-together-for-stateful-automations/

import appdaemon.plugins.hass.hassapi as hass
import mqttapi as mqtt

class MotionActivatedLightsApp(hass.Hass):

	def initialize(self):
		self.motion_sensor = self.args['motion_sensor']
		self.light = self.args['light']
		self.timeout = self.args['timeout']

		self.timer = None
		self.listen_state(self.motion_callback, self.motion_sensor, new = "on")

		# Speculative code in the aims of capturing a button-press.
		self.listen_event(self.pressSwitch_callback, "MQTT_MESSAGE", topic = 'zigbee2mqtt/switch.rumpus')

	def set_timer(self):
		if self.timer is not None:
			self.cancel_timer(self.timer)
		self.timer = self.run_in(self.timeout_callback, self.timeout)

	# Need to fix dimming. Until then - redundant code.
	def is_light_times(self):
		return self.now_is_between("sunset - 00:10:00", "sunrise + 00:10:00")

	def motion_callback(self, entity, attribute, old, new, kwargs):
		self.log("Motion callback - triggered")
		self.turn_on(self.light)
		self.set_timer()

	def timeout_callback(self, kwargs):
		self.log("Timeout callback - triggered")
		self.timer = None
		self.turn_off(self.light)

	def pressSwitch_callback(self, eventname, data, kwargs):
		self.log(data[0])



