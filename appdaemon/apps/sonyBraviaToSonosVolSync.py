import appdaemon.plugins.hass.hassapi as hass
import datetime
import re
import mqttapi as mqtt

# This app exists to slave the (Sonos Playbar + Sub)'s vol settings to match those of the (Sony Bravia) TV's.
# This is a necessary hack, given that the Sony Bravia doesn't have an IR remote, and IR is all that my old Playbar will accept.
#
# On the Bravia turning on (state change to 'Playing'), set vol to a nominal level, and start listeners watch the Bravia's vol state change.
# On the Bravia's vol changing - set the Sonos' vol state to match it.
# On the Bravia turning off. Set the Sonons' vol to zero


class SonyBraviaToSonosVolSyncApp(hass.Hass):

	def initialize(self):
		self.initialVol = 0.20
		self.tvEntityName = "media_player.sony_bravia_tv"
		self.sonosEntityName = "media_player.living_room"
		self.listen_state(self.tvOnOff_callback, self.tvEntityName)
		self.listen_state(self.tvVolChange_callback, self.tvEntityName, attribute = "volume_level")

	def tvOnOff_callback(self, entity, attribute, old, new, kwargs):
		self.tvState = self.get_state(entity_id = self.tvEntityName)
		if (self.tvState == "off"):
			self.set_state(self.tvEntityName, state = "off", attributes = {"volume_level": "0"})
			self.set_state(self.sonosEntityName, state = "off", attributes = {"volume_level": "0"})
		elif (self.tvState == "playing"):
			self.set_state(self.tvEntityName, state = "off", attributes = {"volume_level": self.initialVol})
			self.set_state(self.sonosEntityName, state = "off", attributes = {"volume_level": self.initialVol})

	def tvVolChange_callback(self, entity, attribute, old, new, kwargs):
		self.tvVol = self.get_state(entity_id = self.tvEntityName, attribute = "volume_level")
		self.set_state(self.tvEntityName, state = "on", attributes = {"volume_level": self.tvVol})
