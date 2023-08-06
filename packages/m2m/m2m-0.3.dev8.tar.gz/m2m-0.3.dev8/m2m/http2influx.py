# Source:
# https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# https://gist.github.com/miguelgrinberg/5614326

from datetime import datetime
from flask import Flask, jsonify, abort, make_response, request
import json

#from influxdb_client import InfluxDBClient, Point, WritePrecision
#from influxdb_client.client.write_api import SYNCHRONOUS

with open("devices.json", "r") as fd:
    devices_dict = json.load(fd)

def create_app():
    app = Flask(__name__)

    # Since this is a web service client applications will expect that we always respond with JSON

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


    # TEMPORARY ROUTE FOR DEBUG ###################################################

    # # To test this function we can use the following curl command:
    # # $ curl -i http://localhost:5000/

    # @app.route('/', methods=['GET'])
    # def get_measures():
    #     return "Hello"


    # ADD A MEASURE ###############################################################

    # The request.json will have the request data, but only if it came marked as JSON.
    # If the data isn't there, or if it is there, but we are missing a title item then we return an error code 400, which is the code for the bad request.
    # We then create a new measure dictionary.
    # We tolerate a missing description field, and we assume the done field will always start set to False.
    # We send the measure to InfluxDB, and then respond to the client with the added measure and send back a status code 201,
    # which HTTP defines as the code for "Created".

    # To test this function we can use the following curl command:
    # $ curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/objenious/measure
    # $ curl -i http://localhost:5000/objenious/measure

    # Example of data returned by Objenious:
    #
    # Headers
    # {"Content-Type":"application\/json"}
    # 
    # Body
    # {
    #     'device_id': 1182194,
    #     'group_id': 210,
    #     'group': 'google',
    #     'profile_id': 7,
    #     'profile': 'elsys-ers',
    #     'timestamp': '2022-03-21T10:54:58Z',
    #     'data': {
    #         'humidity': 40,
    #         'light': 440,
    #         'motion': 1,
    #         'temperature': 21.2,
    #         'tension': 3616
    #     },
    #     'device_properties':
    #     {
    #         'appeui': 'ee00000',
    #         'deveui': 'a81758f',
    #         'external_id': ''
    #     },
    #     'lat': 48.0,
    #     'lng': 2.0,
    #     'geolocation_type': 'network',
    #     'geolocation_precision': 1500,
    #     'city_name': 'London',
    #     'city_code': '12345'
    # }

    #@app.route('/objenious/measure', methods=['POST'])
    @app.route('/measure', methods=['POST'])
    def add_measure():
        try:
            json_dict = request.json
            #print(json_dict)

            #device_id = json_dict['device_id']              # 1182194,
            #group_id = json_dict['group_id']                # 210,
            #group = json_dict['group']                      # 'google',
            #profile_id = json_dict['profile_id']            # 7,
            #profile = json_dict['profile']                  # 'elsys-ers',
            timestamp = json_dict['timestamp']              #  '2022-03-21T10:54:58Z',
            humidity = json_dict['data']['humidity']        # 40
            light = json_dict['data']['light']              # 440
            motion = json_dict['data']['motion']            # 1
            temperature = json_dict['data']['temperature']  # 21.2
            tension = json_dict['data']['tension']          # 3616
            co2 = json_dict['data'].get('co2', None)           # 500
            #device_appeui = json_dict['device_properties']['appeui']           # ee0000
            device_deveui = json_dict['device_properties']['deveui']           # a81758
            #device_external_id = json_dict['device_properties']['external_id'] # 
            #lat = json_dict['lat']                                                    # 48.0
            #lng = json_dict['lng']                                                    # 2.0
            #geolocation_type = json_dict['geolocation_type']                          # 'network'
            #geolocation_precision = json_dict['geolocation_precision']                # 1500
            #city_name = json_dict['city_name']                                        # 'London'
            #city_code = json_dict['city_code']                                        # '12345'

            device_type = "ambiant_sensor"  # TODO...
            device_manufacturer = "Elsys"   # TODO...
            device_ref = "ERS-CO2"          # TODO...

            device_dict = devices_dict.get(device_deveui.upper(), {})

            location = device_dict.get('location', 'unknown')
            device_name = device_dict.get('name', 'unknown')

            # INFLUXDB

            measure_dict_list = [
                {
                    "measurement": "temperature",
                    "value": temperature,
                    "unit": "Celsius"
                },
                {
                    "measurement": "humidity",
                    "value": humidity,
                    "unit": "%"
                },
                {
                    "measurement": "co2",
                    "value": co2,
                    "unit": "ppm"
                },
                {
                    "measurement": "light",
                    "value": light,
                    "unit": ""
                },
                {
                    "measurement": "motion",
                    "value": motion,
                    "unit": ""
                },
                {
                    "measurement": "tension",
                    "value": tension,
                    "unit": "mV"
                }
            ]

            for measure_dict in measure_dict_list:
                if measure_dict['value'] is not None:
                    influx_data_str = f"{measure_dict['measurement']},sensor_id={device_deveui},sensor_name={device_name},sensor_type={device_type},sensor_manufacturer={device_manufacturer},device_ref={device_ref},location={location},unit={measure_dict['unit']} value={measure_dict['value']} {timestamp}"
                    print(influx_data_str)

                    # TODO: send "measure" to Influx...
                    # influxdb_token = "..."
                    # org = "..."
                    # bucket = "measures"
                    # client = InfluxDBClient(url="http://localhost:8086", token=influxdb_token)
                    # write_api = client.write_api(write_options=SYNCHRONOUS)
                    # write_api.write(bucket, org, influx_data_str)

            print()

        except Exception as e:
            print("Error", e)
            abort(400)

        return jsonify({'influx_data_str': influx_data_str}), 201


    return app


###############################################################################

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
