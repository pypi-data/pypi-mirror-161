#from emjolnir import mjolnir
from emjolnir.client import *
import random

class gwangjin_wt_dataloader(wt_dataloader) :
    def load_data(self):
        #TODO: Users need to populate list_dict_data according to their data storage system.
        for list_number in range(0,50) :
            line_dict = dict()
            for key_str in self.list_field :
                line_dict[key_str] = random.randrange(10**10,10**10*9)
            self.list_dict_data.append(line_dict)    

if __name__ == '__main__':
    inst_wt_data = gwangjin_wt_dataloader("gwangjin", mqtt_ip="test.mosquitto.org", mqtt_port=1883)
    inst_wt_data.run_service()