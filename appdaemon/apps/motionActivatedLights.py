# Credit where it's due. Taken from:
# https://webworxshop.com/home-assistant-automation-in-depth-fusing-sensors-together-for-stateful-automations/

import appdaemon.plugins.hass.hassapi as hass
import mqttapi as mqtt

# This is my class for emulating the Hue lighting system.
# 'light' is mandatory. If we don't have one, then what exactly is the point?
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
# TODO: When we have both switches and motion sensors (which I do in a small mumber of cases) - need to decide what ti do.
#
# TODO: handle dimming from switches.
#
# TODO: handle periodic dimming schedules generally. I am thinking: 100% from sunrise to 10pm, then 20% until sunrise in 
# common areas, bathrooms. And no changes in the storeroom, bedrooms, etc.

class MotionActivatedLightsApp(hass.Hass):

	def initialize(self):
		self.light = self.args['light']
		self.timeout = self.args['timeout']
		self.timer = None
		if ('motion_sensor' in self.args):
			self.listen_state(self.motion_callback, self.args['motion_sensor'])
		if ('switch' in self.args):
			self.listen_state(self.pressSwitch_callback, self.args['switch'], new = "on-press")

		# Dimmer / Un-dimmer call-backs.
		self.run_daily(self.dimLightsInEvening_callback, "22:00:00")
		self.run_daily(self.unDimLightsInMorning_callback, "sunrise")		

	def set_timer(self):
		if self.timer is not None:
			self.cancel_timer(self.timer)
		self.timer = self.run_in(self.timeout_callback, self.timeout)

	def motion_callback(self, entity, attribute, old, new, kwargs):
		self.log("Motion callback - triggered")
		self.turn_on(self.light)
		self.set_timer()

	def timeout_callback(self, kwargs):
		self.log("Timeout callback - triggered")
		self.timer = None
		self.turn_off(self.light)

	def pressSwitch_callback(self, entity, attribute, old, new, kwargs):
		# I'm getting correct callback invocation.
		# I am not getting light actuation though. Hopefully this is an easy fix.
		self.log('Message received: \'' + str(new) + '\'')
		self.log(entity)
		self.log(attribute)
		self.log(old)
		self.log(new)
		self.log(kwargs)
		if (new == "on-press"):
			# note: setting the state directly changes the state in HA *BUT* doesn't turn
			self.call_service("light/turn_on", entity_id = "light.rumpus1_light")
			self.call_service("light/turn_on", entity_id = "light.rumpus2_light")
		elif (new == "off-press"):
			self.call_service("light/turn_off", entity_id = "light.rumpus1_light")
			self.call_service("light/turn_off", entity_id = "light.rumpus2_light")

	def dimLightsInEvening_callback(self, kwargs):
		self.log("Dimming the lights per the schedule.")

	def unDimLightsInMorning_callback(self, kwargs):
		self.log("Un-dimming the lights per the schedule.")





