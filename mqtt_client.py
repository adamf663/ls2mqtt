import paho.mqtt.client as mqtt

class MQTTServer:
    def __init__(self, host, port, user, pswd, root_topic, debug=True):
        self.root_topic = root_topic
        self.client = mqtt.Client(client_id='ls2mqtt', clean_session=False)
        self.client.username_pw_set(user, pswd)
        if debug==True:
            self.client.on_connect = self.client_connect_callback
            self.client.on_publish = self.client_publish_callback
            self.client.on_message = self.client_message_callback
        self.client.connect(host, port, keepalive=60)
        self.client.loop_start()

    def client_connect_callback(self, client, userdata, flags_dict, rc):
        print(f'Connected with result code {rc}')
        #client.subscribe(f'{self.root_topic}/#')

    def client_publish_callback(self, client, userdata, mid):
        print(f'published.  userdata={userdata}, message id={mid}')

    def client_message_callback(self, client, userdata, msg):
        print(f'client msg {msg.topic}, {msg.payload}')

    def add_callback(self, topic, callback):
        self.client.message_callback_add(topic, callback)

    def publish(self, topic, val):
        msginfo = self.client.publish(f'{self.root_topic}/{topic}', val, retain=True, qos=1)
        assert msginfo.rc==0, f'unexpected rc={msginfo.rc}'
        msginfo.wait_for_publish()
        print(f'published topic={topic}, val={val}, mid={msginfo.mid}')

    def disconnect(self):
        self.client.disconnect()

# for subscribing with callback
class MQTTObj:
    def __init__(self, server, topic, callback):
        self.topic = topic
        self.callback = callback
        self.last_value = None
        server.add_callback(self.topic, self.intermed_callback)
    def intermed_callback(self, client, userdata, msg):
        self.last_value = msg.payload.decode()
        self.callback(self.last_value)


