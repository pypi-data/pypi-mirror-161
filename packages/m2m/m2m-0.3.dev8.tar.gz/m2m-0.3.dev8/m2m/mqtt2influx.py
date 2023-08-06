#!/usr/bin/env python3

# https://pypi.org/project/paho-mqtt/#id2
# https://medium.com/python-point/mqtt-basics-with-python-examples-7c758e605d4

import m2m

import argparse
import paho.mqtt.client as mqtt
import json
import sys
import traceback

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

class MQTT2Influx:

    def __init__(self, config_path, verbose=False):

        self.verbose = verbose

        # Get config

        self.cfg, self.config_path = m2m.config.get_config(config_path)

        # Setup MQTT

        self.mqtt_client = mqtt.Client(self.cfg["mqtt2influx"]["mqtt"]["client_name"])
        self.mqtt_client.on_connect = self.mqtt_on_connect_callback
        self.mqtt_client.on_message = self.mqtt_on_message_callback
        self.mqtt_client.connect(self.cfg["mqtt2influx"]["mqtt"]["broker_address"])

        # Setup InfluxDB

        self.influxdb_org = self.cfg["mqtt2influx"]["influxdb"]["org"]
        self.influxdb_bucket = self.cfg["mqtt2influx"]["influxdb"]["bucket"]

        self.influxdb_client = InfluxDBClient(url=self.cfg["mqtt2influx"]["influxdb"]["url"],
                                              token=self.cfg["mqtt2influx"]["influxdb"]["token"],
                                              org=self.influxdb_org)
        self.influxdb_write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)


    # The callback for when the client receives a CONNACK response from the server.
    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    def mqtt_on_connect_callback(self, mqtt_client, userdata, flags, rc):
        # Print a confirmation message
        print(f'Connected to the MQTT broker at {self.cfg["mqtt2influx"]["mqtt"]["broker_address"]} with result code ' + str(rc))

        # Subscribe to MQTT topics
        for topic_str in self.cfg["mqtt2influx"]["mqtt"]["subscribed_topic_list"]:
            print(f"Subscribe to {topic_str}")
            mqtt_client.subscribe(topic_str)


    def mqtt_on_message_callback(self, client, userdata, message):
        #print(message)

        try:
            topic = message.topic

            device_desc = None
            supervisor_cmd = None

            if len(topic.split("/")) == 5:
                project_name, building_name, zone_name, device_type, device_id = topic.split("/")
            elif len(topic.split("/")) == 6:
                project_name, building_name, zone_name, device_type, device_id, device_desc = topic.split("/")
            elif len(topic.split("/")) == 7:
                project_name, building_name, zone_name, device_type, device_id, device_desc, supervisor_cmd = topic.split("/")
            else:
                raise Exception(f'Wrong topic format {topic} ; expect either "project_name/building_name/zone_name/device_type/device_id" or "project_name/building_name/zone_name/device_type/device_id/device_desc"')

            #timestamp = message.timestamp

            data_str = message.payload.decode('utf-8')
            data_dict = json.loads(data_str)

            if supervisor_cmd is None:
                if device_type in self.cfg["mqtt2influx"]["devices"].keys():
                    for measure_schema_dict in self.cfg["mqtt2influx"]["devices"][device_type]:
                        default_value = measure_schema_dict["default_value"]
                        if default_value == "nan":
                            default_value = float("nan")

                        value = data_dict.get(measure_schema_dict["mqtt_measurement_name"], default_value)
                        if "discrete_value_converter_dict" in measure_schema_dict:
                            discrete_value_converter_dict = measure_schema_dict["discrete_value_converter_dict"]
                            value = int(discrete_value_converter_dict[value])
                        elif "boolean_true_value" in measure_schema_dict:
                            value = 1 if value==measure_schema_dict["boolean_true_value"] else 0
                        elif "boolean_false_value" in measure_schema_dict:
                            value = 0 if value==measure_schema_dict["boolean_false_value"] else 1 

                        data_str = f'{measure_schema_dict["influxdb_measurement_name"]},device_id={device_id},zone_name={zone_name},device_type={device_type},unit={measure_schema_dict["unit"]} value={value}'

                        if self.verbose:
                            print(data_str)

                        self.influxdb_write_api.write(self.influxdb_bucket, self.influxdb_org, [data_str])


        except Exception as e:
            print("Error: ", e, file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)


    def run(self):
        # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a manual interface.
        self.mqtt_client.loop_forever()


def main():
    """The main module execution function.

    Contains the instructions executed when the module is not imported but
    directly called from the system command line.
    """

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="MQTT2Influx Daemon")

    parser.add_argument("--version", "-V", action="store_true",
                        help="Print the M2M Daemons version and exit.")

    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print debug messages.")

    parser.add_argument("--config-path", default=None, metavar="FILE",
                        help="Configuration file path.")

    args = parser.parse_args()

    ###########################################################################

    if args.version:
        print(m2m.get_version())
    else:
        print(f"Starting MQTT2Influx Daemon {m2m.get_version()}")
        daemon = MQTT2Influx(args.config_path, verbose=args.verbose)
        daemon.run()


if __name__ == '__main__':
    main()