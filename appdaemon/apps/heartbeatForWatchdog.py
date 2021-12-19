import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

class HeartbeatForWatchdogApp(hass.Hass):

	def initialize(self):
		self.url = "https://yvg55bdvze.execute-api.ap-southeast-2.amazonaws.com/Prod/heartbeat"
		self.run_every(self.sendHeartbeatMessage_callback, "now", 60)

	def sendHeartbeatMessage_callback(self, kwargs):
		r = requests.get(self.url)
		if (r.status_code == 200):
			self.log("Heartbeat sent.")

