#
# MQTTDevice module
#
# This module loads configuration informtaion about MQTT broker and MQTT Autoconfiguration data about sensors from a
# configuration file.
#
# Version:      0.31
#
# Version       Date            Comment
# 0.31		      2024-01-15	    Minor adjustment to publish availability and device on on connect
# 0.3		        2022-09-08	    Updated version from MQTTSensors to MQTTDevice adding more capabilities.
# 0.2           2022-09-03      Updated version to handle sensor info required by main application.
# 0.1           2022-09-03      Initial version, built to simplify management of MQTT configuration data.
#
import sys, ssl, time, yaml, json
import paho.mqtt.client as mqtt
try:
  from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
  from yaml import Loader, Dumper

#
# MQTT Sensors class
#
class MQTTDevice:
  #
  # Connection handling for MQTT broker
  #
  def _on_connect(self, client, userdata, flags, rc):
    print("Connected to MQTT broker", flush=True)
    # Add relevant subscriptions here :)

    # Share availability status
    self.client.publish(self.cfg['availability_topic'], "online", retain=True)
    self.client.will_set(self.cfg['availability_topic'], "offline", retain=True)

    # Send device autodiscovery information to broker
    for e in self.cfg['entities']:
      self.client.publish(e['discovery_topic'], json.dumps(e['discovery_payload']), retain=True)

  def _on_disconnect(self, client, userdata, rc):
    print("Disconnected from MQTT broker")

  def _on_message(self, client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

  #
  # Constructor
  #
  def __init__(self, config='configuration.yml'):
    # Load configuration file for sensors
    with open(config, 'r') as stream:
      try:
        self.cfg = yaml.load(stream, Loader=Loader)
      except yaml.YAMLError as exc:
        print("Error parsing configuration.yml. Exiting.")
        print(exc)
        sys.exit(1)
      stream.close()

    # Connect to MQTT broker
    self.client = mqtt.Client(self.cfg['clientid'])
    self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    self.client.on_connect = self._on_connect
    self.client.on_disconnect = self._on_disconnect
    self.client.on_message = self._on_message
    self.client.username_pw_set(username=self.cfg['username'],password=self.cfg['password'])
    self.client.connect(self.cfg['host'], self.cfg['port'])
    self.client.loop_start()

  #
  # Get sensors
  #
  def getentities(self):
    return self.cfg['entities']

  #
  # Publish message
  #
  def publish(self, topic, payload):
    self.client.publish(topic, json.dumps(payload))
