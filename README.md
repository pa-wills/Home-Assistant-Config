This is my own personal Home Assistant configuration.

# Background
I started with Apple's HomeKit and Phillips Hue lighting. Apple's apparent commitment to security seemed pretty cool, and Phillips' ecosystem seemed slick, and difficult to screw-up. A friend then introduced me to Home Assistant, and I started using it in Docker before moving recently to hassos.

# Current System
* [Raspberry Pi4](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/), usually running the latest version of HassOS, with several add-ons. I started with a Pi3, but the performance limitations became apparent fairly quickly.
* [Phillips Hue](https://en.wikipedia.org/wiki/Philips_Hue) with a number of bulbs, switches and motion detectors. I recently replaced the Hue Bridge with an AppDaemon class that emulates the basic functions + [Zigbee2MQTT](https://www.zigbee2mqtt.io/).
* Two [Nest Protect](https://en.wikipedia.org/wiki/Google_Nest#Nest_Protect)s. I still have a working token for the now-deprecated Works with Nest API.
* [TP-Link HS100](https://www.tp-link.com/au/home-networking/smart-plug/hs100/) power plugs. They work really well, though the relay in them makes an annoying click.
* Integrations for my Roku and for my LG TV. I have barely-utilised these though.
* Various device_trackers: including [nmap](https://www.home-assistant.io/integrations/nmap_tracker/), [Tile](https://www.home-assistant.io/integrations/tile/), and ios. These are for establishing presence.

# Automations
* I have very rudimentary time-based automations for turning off lights and my TV at various times of day.
* I have sun-based automations for my porch light.
* I have very basic automations that trigger / disable our downstairs lighting when people enter / leave the Home zone.
* I have motion-based automations that alert me when certain zones are entered, and the scope changes depending on Occupancy.
* HassOS automaticlly creates a daily snapshot, which then automatically syncs to Dropbox.
I should say - I am porting most of my [Automations](https://www.home-assistant.io/docs/automation/) to [AppDaemon](https://appdaemon.readthedocs.io/en/latest/); which I intend to use exclusively in future.

# What's Next?
Lots and lots. The immediate development priorities are listed under Issues. I have a basic master plan, but it's mostly in my head. I'll document it in time.

# How the code is organised
I am now experimenting with [GitHub Flow](https://githubflow.github.io/), which I think is probably sensible given that it's just me that's developing this, and given that I often deploy several times per day. 

I made a spectacularly unsuccessful attempt to use [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/). I gave up though because I could not figure out a low-touch way to keep the continuously running branches (principally *master* and *dev*) in sync. And, I realised that I was spending as much time trying to operate these pipelines as I had been spending trying to develop features. Still, it seems like a really elegant model. I just didn't have the necessary patience / skill to get it working.

# Tool Chain
* Any commit will trigger an automatic build on Travis-CI.

All in all, there's nothing unique here. I am just learning as I go, and drawing inspiration from the various people who have already blazed a trail.
