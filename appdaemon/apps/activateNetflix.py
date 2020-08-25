import hassapi as hass
import time

class ActivateNetflixApp(hass.Hass):

def initialize(self):
  # This is hacky, but we will run it off a wrapper script.
  self.listen_state(myCallback, script.activate_netflix)

def myCallback(self, entity, attribute, old, new, kwargs):
  # If the TV is off, turn it on.
  if (self.get_state("media_player.lg_webos_smart_tv") == 'off'):
  	self.toggle("switch.tv_lg_power")
  while(self.get_state("media_player.lg_webos_smart_tv") == 'off'):
  	time.sleep(1)

  # Get the Roku into the playing state.
  if (self.get_state("media_player.roku_yl00at185320") not it ['Idle', 'Standby']):
    self.toggle("switch.roku_home_button")
  while(self.get_state("media_player.roku_yl00at185320") != 'Playing'):
    time.sleep(1)

  self.set_state("media_player.lg_webos_smart_tv", "on", {"Source": "HDMI2"})
  self.set_state("media_player.roku_yl00at185320", "on", {"Source": "Netflix"})
