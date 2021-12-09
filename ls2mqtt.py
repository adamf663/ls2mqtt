import traceback
from mqtt_client import MQTTServer
import datetime
import serial

house_id = 1
mqtt_topic = 'living_sensibly'
receiver_port = '/dev/ttyUSB0'

class ParseSensibleLiving():
    def __init__(self, msg):
        self.device_id = None
        self.sensor_type = None
        self.num_sensors = None
        self.alarms = None
        self.sensors = None
        self.batt = None
        self.valid = False
        self.parse(msg)

    def hex2signed(self, hexstr, bits=16):
        i = int(hexstr, bits)
        if i>>(bits-1):
            return i - (1<<bits)
        else:
            return i

    def hex2bitarray(self, hexstr, bits=16):
        # returns array of boolean
        i = int(hexstr, bits)
        return [bool(i&1<<bit) for bit in range(bits)]

    def parse(self, msg):
        try:
            fields = msg.split(',')
            if fields[0] == 'A7' and int(fields[1]) == house_id :
                self.device_id = fields[2]
                self.sensor_type = int(fields[3])
                self.num_sensors = int(fields[4])
                self.alarms = self.hex2bitarray(fields[5])
                self.sensors = [self.hex2signed(fields[6+s]) / 10 for s in range(self.num_sensors)]
                self.batt = self.hex2signed(fields[6+self.num_sensors]) / 100
                self.valid = True
        except Exception as e:
            print('Parsing exception:')
            print(traceback.format_exc())

    def __bool__(self):
        return self.valid

    def publish(self, mqtt):
        mqtt.publish(
                topic=f'{self.device_id}/sensor_type',
                val=self.sensor_type)
        for sensor in range(len(self.sensors)):
            mqtt.publish(
                topic=f'{self.device_id}/sensor_{sensor}',
                val=self.sensors[sensor])
        mqtt.publish(
                topic=f'{self.device_id}/batt',
                val=self.batt)
        
        mqtt.publish(
                topic=f'{self.device_id}/last_update',
                val=f'{datetime.datetime.today():%Y-%m-%d %H:%M}')

if __name__ == '__main__':
    mqtt = MQTTServer(host="hassio.homenet", port=1883,
                     user='homeauto', pswd='shutupalexa',
                     root_topic='sensible_living')
    while True:
        try:
            with serial.Serial(receiver_port, 9600, timeout=90*60) as ser:
                while True:
                    msg = ser.readline().decode()
                    if msg:
                        print(f"received: {msg}")
                        parsed = ParseSensibleLiving(msg)
                        if parsed:
                            parsed.publish(mqtt)
        except:
            print('jumping jack crash.')
            print(traceback.format_exc())

