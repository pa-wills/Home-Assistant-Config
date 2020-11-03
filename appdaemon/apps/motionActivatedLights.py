# Credit where it's due. Taken from:
# https://webworxshop.com/home-assistant-automation-in-depth-fusing-sensors-together-for-stateful-automations/
# https://webworxshop.com/getting-started-with-appdaemon-for-home-assistant/

import appdaemon.plugins.hass.hassapi as hass
import re
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
# Switches override motion sensors. Specifically, an on-press from a switch will effectively render the motion sensors inert, until
# the light is off-press'd, at which point - the lights go back to being automatic.
#
# TODO: handle dimming from switches.
#
# TODO: handle periodic dimming schedules generally. I am thinking: 100% from sunrise to 10pm, then 20% until sunrise in 
# common areas, bathrooms. And no changes in the storeroom, bedrooms, etc.

class MotionActivatedLightsApp(hass.Hass):

	def initialize(self):
		self.lights = self.args['lights']
		self.timeout = self.args['timeout']
		
		# One timer per instance (not per light).
		# Contains the reference to the timeout_callback, if any.
		self.timer = None

		# A flag to denote whether or not the light's on-state was triggered by a switch.
		self.on_press_triggered = None

		# One brightness value per instance, and we set it every time that we turn a light on.
		self.brightness = 255
		if (self.now_is_between('22:00:00', 'sunrise')):
			self.brightness = 51
		
		if ('motion_sensor' in self.args):
			self.listen_state(self.motion_callback, self.args['motion_sensor'], new = "on")
		if ('switch' in self.args):
			self.listen_state(self.pressSwitch_callback, self.args['switch'])

		# Dimmer / Un-dimmer call-backs.
		if ('dim_schedule' in self.args):
			self.run_daily(self.dimLightsInEvening_callback, "22:00:00")
			self.run_daily(self.unDimLightsInMorning_callback, "sunrise")

	# Kill the existing timeout callback, if the timer is dirty. Then, schedule a new one.
	def set_timer(self):
		if self.timer is not None:
			self.cancel_timer(self.timer)
		self.timer = self.run_in(self.timeout_callback, self.timeout)

	def motion_callback(self, entity, attribute, old, new, kwargs):
		if (self.on_press_triggered == None):
			self.log("Motion callback - triggered")
			for light in self.lights:
				try:
					self.call_service('light/turn_on', entity_id = light, brightness = self.brightness)
				except Exception as e:
					self.log(e)
			self.set_timer()

	def timeout_callback(self, kwargs):
		if (self.on_press_triggered == None):
			self.log("Timeout callback - triggered")
			self.timer = None
			for light in self.lights:
				self.turn_off(light)	

	def pressSwitch_callback(self, entity, attribute, old, new, kwargs):
		try:
			if (new == "on-press"):
				# Setting the state directly changes the state in HA *BUT* doesn't turn it on. Unintuitive.
				for light in self.lights:
					# I use different invocations for lights than I do for switches.
					if (re.search("^light", light) != None):
						self.call_service("light/turn_on", entity_id = light, brightness = self.brightness)
						self.log("Turning on light: " + str(light))
					else:
						self.turn_on(light)
						self.log("Turning on switch: " + str(light))
				# Put the lights in manual mode, cancel any timeout callbacks.
				if self.timer is not None:
					self.cancel_timer(self.timer)
				self.on_press_triggered = 1
			elif (new == "off-press"):
				for light in self.lights:
					if (re.search("^light", light) != None):
						self.call_service("light/turn_off", entity_id = light)
						self.log("Turning off light: " + str(light))
					else:
						self.turn_off(light)						
						self.log("Turning off switch: " + str(light))
				# Re-enable automatic mode.
				self.on_press_triggered = None
			elif (new == "up-press"):
				for light in self.lights:
					if (re.search("^light", light) != None):
						if (self.brightness <= 245):
							self.brightness += 10
						else:
							self.brightness = 255
						self.call_service("light/turn_on", entity_id = light, brightness = self.brightness)
						self.log("Increasing brightness for light: " + str(light))						
			elif (new == "down-press"):
					if (re.search("^light", light) != None):
						if (self.brightness >= 10):
							self.brightness -= 10
						else:
							self.brightness = 0
						self.call_service("light/turn_on", entity_id = light, brightness = self.brightness)
						self.log("Decreasing brightness for light: " + str(light))
		except Exception as e:
			self.log(e)

	# TODO: I think I probably need to break this out into its own class. Or - find a way to do it once - ot once per instance.
	def dimLightsInEvening_callback(self, kwargs):
		self.log("Dimming the lights per the schedule.")
		self.brightness = 51

	def unDimLightsInMorning_callback(self, kwargs):
		self.log("Un-dimming the lights per the schedule.")
		self.brightness = 255





