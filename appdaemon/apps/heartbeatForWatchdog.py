import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

class HeartbeatForWatchdogApp(hass.Hass):

	def initialize(self):
		self.url = "https://api.peterwills.com/Prod/heartbeat"
		self.run_every(self.sendHeartbeatMessage_callback, "now", 5 * 60)

	def sendHeartbeatMessage_callback(self, kwargs):
		r = requests.get(self.url)
		if (r.status_code == 200):
			self.log("Heartbeat sent.")

