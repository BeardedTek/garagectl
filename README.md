# garagectl
Control your Garage Door with a Raspberry Pi, a relay board, apache, and python

# Requirements
## Software
Python 3.9 (other versions may work but untested)
apache2

## Hardware
Raspberry Pi
Relay Board
Garage Door Opener

# More Info
My garage door opener accepts a dry contact to open and close the garage door (one button control)

The basic operation of this will just work as an ordinary clicker.  The magic comes in with Home Assistant.

Each time we command the door to to open or close we tell home assistant what our intention is with a webhook which triggers automations.


# Home Assistant Magic

## Automations

    - id: '1637746423040'
      alias: Garage Door Clicker
      description: ''
      trigger:
      - platform: state
        entity_id: input_boolean.garage_door_clicker
        from: 'off'
        to: 'on'
      condition:
      - condition: state
        entity_id: input_boolean.garage_door_clicker_enable
        state: 'on'
      action:
      - service: shell_command.garage_clicker
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.garage_door_clicker
      - wait_for_trigger:
        - platform: state
          entity_id: binary_sensor.garage_door_home_security_intrusion
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.garage_door_clicker
        mode: single
 
 ***
 
    - id: '1637786879382'
      alias: Garage Door Opening
      description: ''
      trigger:
      - platform: webhook
        webhook_id: garage_door-opening
      condition: []
      action:
      - service: input_text.set_value
        target:
          entity_id: input_text.garage_door_status
        data:
        value: opening
      mode: single
 
 ***
 
    - id: '1637786916834'
      alias: Garage Door Closing
      description: ''
      trigger:
      - platform: webhook
        webhook_id: garage_door-closing
      condition: []
      action:
      - service: input_text.set_value
        target:
          entity_id: input_text.garage_door_status
        data:
        value: closing
      mode: single
 
 ***
 
    - id: '1637790394588'
      alias: Garage Door Open
      description: ''
      trigger:
      - platform: state
        entity_id: input_boolean.garage_door_open
        from: 'off'
        to: 'on'
      condition:
      - condition: state
        entity_id: input_boolean.garage_door_clicker_enable
        state: 'on'
      action:
      - service: shell_command.garage_open
      mode: single
 
 ***
 
    - id: '1637790430181'
      alias: Garage Door Close
      description: ''
      trigger:
      - platform: state
        entity_id: input_boolean.garage_door_close
        from: 'off'
        to: 'on'
      condition:
      - condition: state
        entity_id: input_boolean.garage_door_clicker_enable
        state: 'on'
      action:
      - service: shell_command.garage_close
      mode: single
    - id: '1637812007583'
      alias: Garage Door Enable
      description: ''
      trigger:
      - platform: webhook
        webhook_id: garage_door-enabled
      condition: []
      action:
      - service: input_boolean.turn_on
        target:
        entity_id: input_boolean.garage_door_clicker_enable
      mode: single
 
 ***
 
    - id: '1637812036975'
      alias: Garage Door Disable
      description: ''
      trigger:
      - platform: webhook
        webhook_id: garage_door-disabled
      condition: []
      action:
      - service: input_boolean.turn_off
        target:
        entity_id: input_boolean.garage_door_clicker_enable
      mode: single

## shell scripts
Place these inside your configuration.yml

    shell_command:
      garage_clicker: curl -X GET http://<garagectl-url>/cgi-bin/testpy.cgi?operate=true
      garage_open: curl -X GET http://<garagectl-url>/cgi-bin/testpy.cgi?function=open
      garage_close: curl -X GET http://<garagectl-url>/cgi-bin/testpy.cgi?function=close
      garage_status: curl -X GET http://<garagectl-url>/cgi-bin/testpy.cgi?function=status
