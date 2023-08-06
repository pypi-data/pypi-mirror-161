from dataloader import *

class structured_dl(dataloader) :
    
    @abstractmethod
    def __init__(self, name, re_type, mqtt_ip, mqtt_port):
        self.mqtt_channel = "/emjolnir/sdata/" + name +"/#"
        super().__init__(name, re_type, mqtt_ip, mqtt_port)
    
    def insert_data(self) :
        print("TODO : insert_data")


class structured_wt_dl(structured_dl) :
    
    def __init__(self, name, mqtt_ip, mqtt_port):
        self.name = name
        self.list_output_field = ["CapaP",	"SetP",	"Freq",	"P", "PitchAngle1", "PitchAngle2",
                           "PitchAngle3", "RotorSpeed", "Torque", "V", "WindDirection",
                           "WindSpeed", "YawAngle"]        
        super().__init__(name, "wt", mqtt_ip, mqtt_port)
        
class structured_pv_dl(structured_dl) :
    
    def __init__(self, name, mqtt_ip, mqtt_port):
        self.name = name
        self.list_output_field = ["seq", "datetime", "location", "inverter_num", "Efficiency",
                            "Freq", "Idc", "Ir", "_Is", "It", "P",
                            "PFr", "PFs", "PFt", "Psum", "Temp", "Vdc", "Vr", "Vs", "Vt",]
        super().__init__(name, "pv", mqtt_ip, mqtt_port)