import sys
sys.path.append("/home/jerryin/jupyter_proj/csgo/")

from Util.util import Constant
from Util import util
from Ip.rawIpPool import raw_ip_pool
import time
import requests
import pickle
# import kdl


def getIps(num: int) -> list:
    ips = []
    for i in range(0, num):
        ips.append(getIp())
    return ips

def getIp() -> str:
    ip = Constant.client.get_dps(1, sign_type='hmacsha1', format='json')[0]
    while not checkIpAlive(ip):
        ip = Constant.client.get_dps(1, sign_type='hmacsha1', format='json')[0]
    # return ip
    return '139.9.119.20:80'

def checkIpsAlive(ips: list) -> dict:
    '''
        ips: ip list, does not contain http:
    '''
    # validity = Constant.client.check_dps_valid(ips)
    # return validity
    return True

def checkIpAlive(ip: str) -> bool: 
    '''
        ip: 127.0.0.1:8080
    '''
    # validity =  Constant.client.check_dps_valid(ip)[ip]
    proxyValid = checkProxy(ip)
    # return validity and proxyValid
    return proxyValid

def checkProxy(ip: str) -> bool: # ip like 127.0.0.1:8080
    try:
        proxy = Constant.getProxy(ip)
        
        session = requests.session()
        session.proxies.update(proxy)

        response = session.get(Constant.ip_check_addr)
        if response.text.replace('\n','').replace('\r','') == ip.split(":")[0]: # response.text like 101.37.22.207
            return True
        return False
    except:
        return False
    # print(response.text) # return 101.37.22.207
# https://icanhazip.com/  https://httpbin.org/ip  https://api-bdc.net/data/client-ip

'''
class Ip(object): # one single ip object
    def __init__(self, ip, lag):
        self.ip = ip
        self.proxies = util.getProxy(self.ip)
        # self.is_alive = self.checkAlive()
        self.check_time = time.time()
        self.lag = lag
        # self.is_used = False
    
class IpPool(object): # ip pool object
    def __init__(self, ip_num):
        self.raw_ip_array = raw_ip_pool
        self.ip_pool = self.getIpPool(ip_num)
        self.saveIpPool(self.ip_pool)
    
    def __getitem__(self, index):
        return self.ip_pool[index]
    
    def __len__(self):
        return len(self.ip_pool)

    def getAnIp(self):
        ip_pool = self.getIpPool(1)
        _ip = ip_pool[0]
        ip_pool.remove(_ip)
        self.saveIpPool(ip_pool)
        return _ip

    def remove(self, ip):
        self.ip_pool.remove(ip)
    
    def getIpPool(self, ip_num): # store all ip objects into an array
        ip_pool = self.getIpPoolFromDisk()
        ip_pool_len = len(ip_pool)
        if(ip_pool_len >= ip_num):
            return ip_pool
        res_len = ip_num - ip_pool_len
        new_ip_pool = Constant.client.get_dps(res_len, sign_type='hmacsha1', format='json')
        res_len = len(new_ip_pool)
        for i in range(0, res_len):
            new_ip_pool[i] =  'http://' + new_ip_pool[i]
        
        # print(new_ip_pool)
        
        for index in range(0, res_len):
            is_alive, lag_time = util.checkAlive(util.getProxy(new_ip_pool[index]))
            if is_alive:
                ip_pool.append(Ip(new_ip_pool[index], lag_time))
        return ip_pool
    
    def getIpPoolFromDisk(self):
        try:
            with open(Constant.ip_pool_dir, 'rb') as fin: 
                return pickle.load(fin)
        except:
            return []

    def saveIpPool(self, ip_pool): # save the array into a file called ipPool.pkl
        with open(Constant.ip_pool_dir, 'wb') as fout:
            pickle.dump(ip_pool, fout, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    IpPool(30)
'''