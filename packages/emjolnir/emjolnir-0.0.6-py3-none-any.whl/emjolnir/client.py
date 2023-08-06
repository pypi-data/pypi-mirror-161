from abc import *
import os
import paho.mqtt.client as mqtt

class re_dataloader(metaclass=ABCMeta) :
    
    @abstractmethod
    def __init__(self, name, mqtt_ip, mqtt_port):
        self.re_type = "none"
        self.list_field = list()
        self.list_dict_data = list()    
        self.cur_path = os.path.dirname(os.path.abspath(__file__))
        self.mqtt_ip = mqtt_ip
        self.mqtt_port = mqtt_port
    
    @abstractmethod
    def load_data(self):
        pass
    
    def check_field(self):
        print(self.list_dict_data)
    
    def run_service(self):
        self.load_data()
        self.check_field()
        def on_connect(client, userdata, flags, rc):
            print("Connected with result code : "+str(rc))
            client.subscribe("mqtt/"+ self.name +"/#")

        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(self.mqtt_ip, self.mqtt_port, 60)

        client.loop_forever()

class wt_dataloader(re_dataloader) :
    
    def __init__(self, name, mqtt_ip, mqtt_port):
        super().__init__(self, mqtt_ip, mqtt_port)
        self.re_type = "wt"
        self.name = name
        self.list_field = ["seq",
                            "datetime",
                            "location",
                            "inverter_num",
                            "Efficiency",
                            "Freq",
                            "Idc",
                            "Ir",
                            "_Is",
                            "It",
                            "P",
                            "PFr",
                            "PFs",
                            "PFt",
                            "Psum",
                            "Temp",
                            "Vdc",
                            "Vr",
                            "Vs",
                            "Vt",]
        
        