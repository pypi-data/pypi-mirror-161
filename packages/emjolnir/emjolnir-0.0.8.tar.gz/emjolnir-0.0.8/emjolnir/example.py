from client import *
#from emjolnir.client import *
import random

class gwangjin_wt_sdl(structured_wt_dl) :
    def load_data(self):
        #TODO: Users need to populate list_dict_data according to their data storage system.
        for _ in range(0,50) :
            line_dict = dict()
            for key_str in self.list_output_field :
                line_dict[key_str] = random.randrange(10**10,10**10*9)
            self.list_dict_data.append(line_dict)
            
class dongbok_pv_sdl(structured_pv_dl) :
    def load_data(self):
        #TODO: Users need to populate list_dict_data according to their data storage system.
        for _ in range(0,50) :
            line_dict = dict()
            for key_str in self.list_output_field :
                line_dict[key_str] = random.randrange(10**10,10**10*9)
            self.list_dict_data.append(line_dict)    


class gwangjin_wt_cae(cae_wt_dl) :
    def load_data(self):
        #TODO: Users need to populate list_dict_data according to their data storage system.
        for _ in range(0,50) :
            line_dict = dict()
            for key_str in self.list_output_field :
                line_dict[key_str] = random.randrange(10**10,10**10*9)
            self.list_dict_data.append(line_dict)        

class dongbok_pv_cae(cae_pv_dl) :
    def load_data(self):
        #TODO: Users need to populate list_dict_data according to their data storage system.
        for _ in range(0,50) :
            line_dict = dict()
            for key_str in self.list_output_field :
                line_dict[key_str] = random.randrange(10**10,10**10*9)
            self.list_dict_data.append(line_dict)      

if __name__ == '__main__':
    inst_wt_sdl = gwangjin_wt_sdl("gwangjin", mqtt_ip="test.mosquitto.org", mqtt_port=1883)
    inst_wt_sdl.run_service()
    inst_pv_sdl = dongbok_pv_sdl("dongbok", mqtt_ip="test.mosquitto.org", mqtt_port=1883)
    inst_pv_sdl.run_service()
    
    isnt_wt_cae = gwangjin_wt_cae("gwangjin", mqtt_ip="test.mosquitto.org", mqtt_port=1883)
    isnt_wt_cae.run_service()
    isnt_pv_cae = dongbok_pv_cae("dongbok", mqtt_ip="test.mosquitto.org", mqtt_port=1883)
    isnt_pv_cae.run_service()