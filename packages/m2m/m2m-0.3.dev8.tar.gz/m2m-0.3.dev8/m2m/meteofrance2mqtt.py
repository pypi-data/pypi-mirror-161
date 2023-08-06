#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# C.f. http://theautomatic.net/2019/01/19/scraping-data-from-javascript-webpage-python/

# pip install requests-html

import m2m

# import HTMLSession from requests_html
from requests_html import HTMLSession

import argparse
import json
import paho.mqtt.client as mqtt
import sys
import time
import traceback


class Meteofrance2MQTT:

    def __init__(self, config_path, verbose=False):

        self.verbose = verbose
        self.mqtt_ready = False

        # Get config

        self.cfg, self.config_path = m2m.config.get_config(config_path)

        self.city = self.cfg["meteofrance2mqtt"]["city"]
        self.zipcode = self.cfg["meteofrance2mqtt"]["zipcode"]
        self.sleep_time_sec = self.cfg["meteofrance2mqtt"]["sleep_time_sec"]
        self.mqtt_topic_root = self.cfg["meteofrance2mqtt"]["mqtt"]["mqtt_topic_root"]

        # Setup MQTT

        self.mqtt_client = mqtt.Client(self.cfg["meteofrance2mqtt"]["mqtt"]["client_name"])
        self.mqtt_client.on_connect = self.mqtt_on_connect_callback
        self.mqtt_client.connect(self.cfg["meteofrance2mqtt"]["mqtt"]["broker_address"])


    # The callback for when the client receives a CONNACK response from the server.
    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    def mqtt_on_connect_callback(self, mqtt_client, userdata, flags, rc):
        # Print a confirmation message
        print(f'Connected to the MQTT broker at {self.cfg["meteofrance2mqtt"]["mqtt"]["broker_address"]} with result code ' + str(rc))
        self.mqtt_ready = True


    def get_weather(self):

        # GET HTML ################################################################

        # create an HTML Session object
        session = HTMLSession()

        # Use the object above to connect to needed webpage
        resp = session.get(f"https://meteofrance.com/previsions-meteo-france/{self.city}/{self.zipcode}")

        # Run JavaScript code on webpage
        resp.html.render(30)

        # PARSE HTML ##############################################################

        # To get weather forecast too: [x.text for x in resp.html.xpath("//div[@class='weather_temp']/p")]
        temperature = int(resp.html.xpath("//div[@class='weather_temp']/p")[0].text.replace("°", ""))

        return temperature
    

    def publish_weather(self, weather_dict):
        topic = f"{self.mqtt_topic_root}{self.city}/weather/meteofrance"
        payload = json.dumps(weather_dict)
        #self.mqtt_client.publish(topic, payload=payload, qos=2, retain=False)
        self.mqtt_client.publish(topic, payload=payload)


    def run(self):
        while True:
            try:
                temperature = self.get_weather()
                weather_dict = {
                    "temperature": temperature
                }
                self.publish_weather(weather_dict)
            except Exception as e:
                print("Error: ", e, file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)
            
            time.sleep(self.sleep_time_sec)


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
        print(f"Starting meteofrance2MQTT Daemon {m2m.get_version()}")
        daemon = Meteofrance2MQTT(args.config_path, verbose=args.verbose)

        #while not daemon.mqtt_ready:
        #    print("Waiting for MQTT connexion...")
        #    time.sleep(10)

        time.sleep(3)
        daemon.run()


if __name__ == '__main__':
    main()