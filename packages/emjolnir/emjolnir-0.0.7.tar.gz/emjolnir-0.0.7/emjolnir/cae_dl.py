from dataloader import *

class cae_dl(dataloader) :
    
    def __init__(self, name, re_type, mqtt_ip, mqtt_port):
        self.mqtt_channel = "/emjolnir/cae/" + name +"/#"
        super().__init__(name, re_type, mqtt_ip, mqtt_port)
    
    def insert_data(self) :
        print("TODO : insert_data")

class cae_wt_dl(cae_dl) :
    
    def __init__(self, name, mqtt_ip, mqtt_port):
        self.list_output_field = ["CapaP",	"SetP",	"Freq",	"P", "PitchAngle1", "PitchAngle2",
                           "PitchAngle3", "RotorSpeed", "Torque", "V", "WindDirection",
                           "WindSpeed", "YawAngle"]
        super().__init__(name, "wt", mqtt_ip, mqtt_port)
        
class cae_pv_dl(cae_dl) :
    
    def __init__(self, name, mqtt_ip, mqtt_port):
        self.list_output_field = ["seq", "datetime", "location", "inverter_num", "Efficiency",
                            "Freq", "Idc", "Ir", "_Is", "It", "P",
                            "PFr", "PFs", "PFt", "Psum", "Temp", "Vdc", "Vr", "Vs", "Vt",]
        super().__init__(name, "pv", mqtt_ip, mqtt_port)