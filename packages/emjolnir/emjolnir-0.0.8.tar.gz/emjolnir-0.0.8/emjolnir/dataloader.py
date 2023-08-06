from abc import *
import os
import paho.mqtt.client as mqtt
import threading


class dataloader_interface(metaclass=ABCMeta) :
    @abstractmethod
    def __init__(self, name, re_type, mqtt_ip, mqtt_port):
        self.name = name
        self.re_type = re_type
        self.list_output_field = list()
        self.list_dict_data = list()    
        self.cur_path = os.path.dirname(os.path.abspath(__file__))
        self.mqtt_ip = mqtt_ip
        self.mqtt_port = mqtt_port

    @abstractmethod
    def load_data(self, startdate, enddate):
        pass
    
    @abstractmethod
    def insert_data(self) :
        pass 


class dataloader(dataloader_interface) :    
    def check_field(self):
        for dict_data in self.list_dict_data :
            for key in self.list_output_field :
                list_dict_data = list(dict_data.keys())
                if list_dict_data.count(key) == 0 :
                    return False
        return True
    
    def run_service(self):
    
        def test_func() :
            self.load_data()
            if self.check_field() == True :
                self.insert_data()
        test_func()

        def mqtt_loop():
            client = mqtt.Client()
            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.connect(self.mqtt_ip, self.mqtt_port, 60)
            client.loop_forever()

        threading.Thread(target=mqtt_loop).start()

    
    def on_message(self, client, userdata, msg):
        payload = str(msg.payload)
        print(msg.topic+" "+payload)
        if payload[0:3] == "load" :
            startdate = payload.split("-")[1]
            enddate = payload.split("-")[2]
            self.load_data(startdate, enddate)
            if self.check_field() == True :
                self.insert_data()
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code : "+str(rc))
        client.subscribe(self.mqtt_channel)
        print("Channel name : " + self.mqtt_channel)