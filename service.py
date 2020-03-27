import json
import os
import requests
import sys
from threading import Thread
import time

uri = 'https://api.thinger.io/v1/users/<user>/buckets/<bucket_id>/data?authorization=<auth_key>'
if len(sys.argv) != 2:
    print('Usage {0} <uri>'.format(sys.argv[0]))
    print('  uri: {0}'.format(uri))
    exit()

rest_uri = sys.argv[1]

class Sensor(object):
    def __init__(self):
        self.path = self.get_path()
    def get_path(self):
        BASE = '/sys/bus/w1/devices/'
        FILE = '/w1_slave'
        directories = os.listdir(BASE)
        for directory in directories:
            if directory.startswith('28'):
                return BASE + directory + FILE
        return None
    def raw(self):
        with open(self.path, 'r') as f:
            return f.readlines()
    def temperature(self):
        raw = self.raw()
        while raw[0].strip()[-3:] != 'YES':
            time.sleep(0.5)
            raw = self.raw()
        return float(raw[1].strip()[-5:]) / 1000

class Service(Thread):
    def __init__(self, sensor):
        Thread.__init__(self)
        self.sensor = sensor
        self.running = True

    def run(self):
        while self.running:
            temp = self.sensor.temperature()
            try:
                payload = { 'temperature_c' : temp }
                header = { 'content-type': 'application/json' }
                response = requests.post(rest_uri, data=json.dumps(payload), headers=header)
                print(response.text)
            except Exception, e:
                print(e)
            print(temp)
            time.sleep(60)

srv = Service(Sensor())
#srv.daemon = True
srv.start()
