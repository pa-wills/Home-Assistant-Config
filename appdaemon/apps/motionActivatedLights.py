# Credit where it's due. Taken from:
# https://webworxshop.com/home-assistant-automation-in-depth-fusing-sensors-together-for-stateful-automations/

import appdaemon.plugins.hass.hassapi as hass
import mqttapi as mqtt

# This is my class for emulating the Hue lighting system.
# 'lights' is mandatory. it's a list, with >= 1 elements.
# 'timeout' is mandatory for the moment, but likely shouldn't be.
# 'motion_sensor' and 'switch' are optional. Not all rooms have either.
# 'dim_schedule' is optional. If it's present, and true, then we run the callbacks on this light 
# (how will this work with groups?) Perhaps 'light' should be a list, which we iterate through.
#
# When triggered from a motion sensor, the paired light turns on for the timeout period, then off again.
# The exception being when another motion event is tripped ahead of the reset. In this case, the most recent one (seems to be) used.
#
# TODO: When triggered from a switch - the light remains on indefinitely.
#
# TODO: When we have both switches and motion sensors (which I do in a small mumber of cases) - need to decide what to do.
#
# TODO: handle dimming from switches.
#
# TODO: handle periodic dimming schedules generally. I am thinking: 100% from sunrise to 10pm, then 20% until sunrise in 
# common areas, bathrooms. And no changes in the storeroom, bedrooms, etc.

class MotionActivatedLightsApp(hass.Hass):

	def initialize(self):
		self.lights = self.args['lights']
		self.timeout = self.args['timeout']
		
		# One timer per instance (not per light). Fully bright by default.
		self.timer = 255

		# One brightness value per instance, and we set it every time that we turn a light on.
		self.brightness = None
		if (self.now_is_between('sunrise', '22:00:00')):
			self.brightness = 255
		else:
			self.brightness = 51
		
		if ('motion_sensor' in self.args):
			self.listen_state(self.motion_callback, self.args['motion_sensor'], new = "on")
		if ('switch' in self.args):
			self.listen_state(self.pressSwitch_callback, self.args['switch'])

		# Dimmer / Un-dimmer call-backs.
		if ('dim_schedule' in self.args):
			self.run_daily(self.dimLightsInEvening_callback, "22:00:00")
			self.run_daily(self.unDimLightsInMorning_callback, "sunrise")

	def set_timer(self):
		if self.timer is not None:
			self.cancel_timer(self.timer)
		self.timer = self.run_in(self.timeout_callback, self.timeout)

	def motion_callback(self, entity, attribute, old, new, kwargs):
		self.log("Motion callback - triggered")
		for light in self.lights:
			self.call_service('light/turn_on', entity = light, brightness = self.brightness)
		self.set_timer()

	def timeout_callback(self, kwargs):
		self.log("Timeout callback - triggered")
		self.timer = None
		for light in self.lights:
			self.turn_off(light)

	def pressSwitch_callback(self, entity, attribute, old, new, kwargs):
		self.log('Message received: \'' + str(new) + '\'')
		self.log('entity: ' + str(entity))
		self.log('attribute: ' + str(attribute))
		self.log('old: ' + str(old))
		self.log('new: ' + str(new))
		self.log(kwargs)
		
		try:
			if (new == "on-press"):
				# note: setting the state directly changes the state in HA *BUT* doesn't turn
				for light in self.lights:
					self.call_service("light/turn_on", entity_id = light, brightness = self.brightness)
			elif (new == "off-press"):
				for light in self.lights:
					self.call_service("light/turn_off", entity_id = light)
		except exception as e:
			self.log(e)


	# TODO: I think I probably need to break this out into its own class. Or - find a way to do it once - ot once per instance.
	def dimLightsInEvening_callback(self, kwargs):
		self.log("Dimming the lights per the schedule.")
		self.brightness = 51

	def unDimLightsInMorning_callback(self, kwargs):
		self.log("Un-dimming the lights per the schedule.")
		self.brightness = 255





