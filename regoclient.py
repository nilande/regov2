#!/usr/bin/env python3
import os, signal, sys, time
from subprocess import Popen, PIPE
import mqttdevice, regointerface

def main():
  # Initialize MQTT connection and load sensors
  md = mqttdevice.MQTTDevice()
  entities = md.getentities()

  # Initiate serial rego interface
  ri = regointerface.RegoInterface()

  # Enter program loop
  while True:
    # Identify which entities are due for polling
    due = list(filter(lambda e:
        # An entity should be included if 'pollintervall' seconds has passed since last poll, or it has not been polled before
        time.time() >= e['pollinterval'] + e['lastpoll'] if 'lastpoll' in e else True
      , entities))

    # Sort due entities such that those with low pollinterval are prioritized
    due.sort(key = lambda x: x['pollinterval'])

    numdue = len(due)

    # Limit polling to X number of registers at a time
    del due[15:]

    print("Polling ", len(due), " out of ", numdue, " due values to refresh...")

    # Loop through entities to be polled
    for e in due:
      # Update lastpoll time and fetch information
      e['lastpoll'] = time.time()
      val = ri.query_register(e['address'].to_bytes(2, "big"))

      # Process result differently based on datatype
      match e['valtype']:
        case 'boolean':
          if val == 1:
            md.publish(f"rego/{e['address']:#0{6}x}/state", val)
          elif val == 0:
            md.publish(f"rego/{e['address']:#0{6}x}/state", val)
        case 'fraction':
          if val: md.publish(f"rego/{e['address']:#0{6}x}/state", val/10)
        case 'temperature':
          if val: md.publish(f"rego/{e['address']:#0{6}x}/state", val/10)
        #case _:
        #  print("Unknown type")

    time.sleep(30)

if __name__ == "__main__":
    main()
