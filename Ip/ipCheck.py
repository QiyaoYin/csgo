import sys
sys.path.append("/home/jerryin/jupyter_proj/csgo/")

from Util.util import Constant
from Util import util
from Ip.rawIpPool import raw_ip_pool
import time
import requests
import pickle

class Ip(object): # one single ip object
    def __init__(self, ip):
        self.ip = ip
        self.proxies = util.getProxy(self.ip)
        self.is_alive = self.checkAlive()
        self.check_time = time.time()
        self.lag = 0
        self.is_used = False
        
    def checkAlive(self): # check if ip alive or dead
        current_time = time.time()
        resp = requests.get(Constant.ip_check_addr, self.proxies)
        self.lag = time.time() - current_time
        print(resp.status_code)
        return True if resp.status_code == 200 else False
    
class IpPool(object): # ip pool object
    def __init__(self):
        self.raw_ip_array = raw_ip_pool
        self.ip_pool = self.getIpPool()
        self.saveIpPool(self.ip_pool)
    
    def __getitem__(self, index):
        return self.ip_pool[index]
    
    def __len__(self):
        return len(self.ip_pool)

    def getIpPool(self):# store all ip objects into an array
        ip_pool = []
        for index in range(0, len(self.raw_ip_array)):
            ip_pool.append(Ip(self.raw_ip_array[index]))
        return ip_pool
    
    def saveIpPool(self, ip_pool): # save the array into a file called ipPool.pkl
        with open(Constant.ip_pool_dir, 'wb') as fout:
            pickle.dump(ip_pool, fout, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    IpPool()