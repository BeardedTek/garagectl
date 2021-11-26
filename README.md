# garagectl
Control your Garage Door with a Raspberry Pi, a relay board, apache, and python

# Requirements
# Software
Python 3.9 (other versions may work but untested)
apache2

# Hardware
Raspberry Pi
Relay Board
Garage Door Opener

# More Info
My garage door opener accepts a dry contact to open and close the garage door (one button control)

The basic operation of this will just work as an ordinary clicker.  The magic comes in with Home Assistant.

Each time we command the door to to open or close we tell home assistant what our intention is with a webhook which triggers automations.

Eventually I will get the documentations about that on here, but for now I needed to get this saved and off my home setup in case of a data failure.
