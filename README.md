This is my own personal Home Assistant configuration.

# Background
My initial automation forays were exlusively with Apple's HomeKit and Phillips Hue lighting. I was attracted to Apple's apparent commitment to security, and also the fairly slick Phillips ecosystem. A friend introduced me to Home Assistant, and I started using it in Docker before moving recently to hassos.

# Current System
* Raspberry Pi3, running a fairly-recent version of HassOS, with several add-ons.
* Phillips Hue with a number of bulbs, switches and motio detectors. I also have a Go in my living room, but it's basically a doorstop.
* Two Nest Protects. I still have a working token for the now-deprecated Works with Nest API.
* TP-Link power plugs. They work really well, though the relay in them makes an annoying click.
* Integrations for my Roku and for my LG TV. I have barely-utilised these though.
* Various device_trackers: including nmap, Tile, and ios. These are for establishing presence.

# Automations
* I have very rudimentary time-based automations for turning off lights and my TV at various times of day.
* I have sun-based automations for my porch light.
* I have very basic automations that trigger / disable our downstairs lighting when people enter / leave the Home zone.
* HassOS automaticlly creates a daily snapshot, which then automatically syncs to Dropbox.

# What's Next?
Lots and lots. The immediate development priorities are listed under Issues. I have a basic master plan, but it's mostly in my head. I'll document it in time.

# How the code is organised
* Master - this branch is always stable and releaseable. And, it goes without saying, this is the where all branches should ultimately merge back to. And, also, this will be the branch I will generally use in production.
* Development - this will be the main thread for, you guessed it, development, and it is branched from Master. I will commit small items / bug-fixes to this branch, but otherwise intend to use the following for larger items....
* Feature branches - where I've got something relatively large to create, I will branch from Development.
* Release branches - these feel superfluous for the moment, but perhaps I will do this later once the codebase becomes bigger.

# Tool Chain
* Any commit will trigger an automatic build on Travis-CI.

All in all, there's nothing unique here. I am just learning as I go, and drawing inspiration from the various people who have already blazed a trail.
