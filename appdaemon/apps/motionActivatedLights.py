# Credit where it's due. Taken from:
# https://webworxshop.com/home-assistant-automation-in-depth-fusing-sensors-together-for-stateful-automations/

class MotionActivatedLightsApp(hass.Hass):

	def initialize(self):
		self.motion_sensor = self.args['motion_sensor']
		self.light = self.args['light']
		self.timeout = self.args['timeout']

		self.timer = None
		self.listen_state(self.motion_callback, self.motion_sensor, new = "on")

	def set_timer(self):
		if self.timer is not None:
			self.cancel_timer(self.timer)
		self.timer = self.run_in(self.timeout_callback, self.timeout)

	def is_light_times(self):
		return self.now_is_between("sunset - 00:10:00", "sunrise + 00:10:00")

	def motion_callback(self, entity, attribute, old, new, kwargs):
		if self.is_light_times():
			self.turn_on(self.light)
			self.set_timer()

	def timeout_callback(self, kwargs):
		self.timer = None
		self.turn_off(self.light)
