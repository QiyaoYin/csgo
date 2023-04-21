import sys
sys.path.append("/home/jerryin/jupyter_proj/csgo/")

from Util.util import Constant, getMilliTime, Buyer, getProxy
from Util import util
import time
import requests
import pickle
from Account.accountPool import AccountPool, Account
import threading
from hyper.contrib import HTTP20Adapter
import random
import math
ITEM_ID_LIST = []

class MyThread(threading.Thread):
    def __init__(self, threadID, account, sleepSec, goods_id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.account = account
        self.sleepSecRange = [sleepSec / 2, sleepSec] # sleep from accountNum / 2 to accountNum sec.
        self.goods_id = goods_id

        self.sessions = requests.session() # the session for accessing buff
        self.sessions.mount(Constant.domain, HTTP20Adapter())
        self.sessions.headers = Constant.buff_req_headers

    def get_goods_data(self):
        # 裂空武器箱:781534
        _path = Constant.getGoodsAddr(self.goods_id, getMilliTime())
        _url = Constant.domain + _path
        _header = {
            ':method': 'GET',
            ':path': _path,
            'cookie': self.account.cookie + 'csrf_token=' + self.account.csrf_token,
            'referer': Constant.domain + '/goods/' + self.goods_id,
        }
        resp = self.sessions.get(_url, headers = _header, proxies = getProxy(self.account.ip))
        if resp.status_code == 404:
            print('update the account related ip from ' + self.account.ip + ' to ...\n')
            self.account.updateIp()
            return self.get_goods_data()
        # print(resp.headers)
        # self.account.csrf_token = resp.headers.get(b'set-cookie').decode("utf-8").split(';')[0].split('=')[1]
        # self.account.csrf_token = resp.cookies.get_dict()['csrf_token']
        try:
            self.account.csrf_token = resp.headers.get(b'set-cookie').decode("utf-8").split(';')[0].split('=')[1]
        except:
            pass
        return resp

    def getStatus(self, resp: object) -> int:
        '''
        return: 
            0: login and market available
            1: did not login
            -1: can not access market or other problems  
        '''
        code = resp.json()['code']
        if code == 'OK' or code == 'ok':
            return 0
        elif code == 'Login Required':
            return 1
        else:
            return -1 
    
    def run(self):
        print ("Starting thread: " + self.threadID + ' ip : ' + self.account.ip + ' phone number : ' + self.account.phone + '\n')
        
        while(True):
            try:
                resp = self.get_goods_data()
                code = self.getStatus(resp)
                if code == 1:
                    while not self.account.login():
                        continue
                elif code == -1:
                    self.account.blockPhone()
                    while not self.account.login():
                        continue
                
                item = resp.json()['data']['items'][0]
                print(self.threadID + ' ' + item['price'])
                if(float(item['price']) < Constant.goods['bar'] and item['id'] not in ITEM_ID_LIST):
                    ITEM_ID_LIST.append(item['id'])
                    
                    Buyer.buy_goods(self.goods_id, item['id'], item['price'])
                    print('buy the goods, goods id: ' + self.goods_id + 'price is :' + item['price'] + '\n')
                    Buyer.sendMessage(item['price'])
                    # print('get_goods_data: \n')
                    # print(item)
                
                time.sleep(random.randint(int(self.sleepSecRange[0]), int(self.sleepSecRange[1])))
                # time.sleep(10)
            except BaseException as e:
                print('exception in the MyThread class: \n')
                print(e)
                continue

class Main(object):
    def __init__(self, account_num: int):
        # self.account_list = self.getAccountPool()
        # self.account_len = len(self.account_list)
        # self.ipPool = self.getIpPool()
        self.accountPool = AccountPool(account_num)
        self.saveAccountPool()
        self.run()

    def saveAccountPool(self) -> None:
        with open(Constant.account_pool_dir, 'wb') as fout:
            pickle.dump(self.accountPool, fout, pickle.HIGHEST_PROTOCOL)
    
    def run(self) -> None:
        index = 0
        print('account pool num: ' + str(self.accountPool.account_num))
        for account in self.accountPool:
            time.sleep(1)
            MyThread('Thread ' + str(index), account, self.accountPool.account_num, Constant.goods['id']).start()
            index += 1
        # for i in range(0, self.accountPool.account_num):
        #     if not self.account_list[i].is_login:
        #         continue
        #     if not self.account_list[i].is_market:
        #         continue
        #     time.sleep(1)
        #     is_alive, lag_time = util.checkAlive(self.account_list[i].ipObj.proxies)
        #     if not is_alive:
        #         print('ip ' + self.account_list[i].ipObj.ip + ' is not alive \n')
        #         self.account_list[i].ipObj = self.ipPool.getAnIp()
        #     if lag_time > 20:
        #         print('ip ' + self.account_list[i].ipObj.ip + ' lag too long \n')
        #         self.account_list[i].ipObj = self.ipPool.getAnIp()
            
        #     MyThread('Thread ' + str(i), self.account_list[i], self.account_len, '45237').start()
    
    # def getIpPool(self):
    #     return IpPool(0)

    # def getAccountPool(self):
    #     with open(Constant.account_pool_dir, 'rb') as fin: 
    #         accountPool = pickle.load(fin)
    #         return self.upateAccountPool(accountPool)
    
    # def upateAccountPool(self, accountPool):
    #     _now = time.time()
    #     for account in accountPool:
    #         if (math.ceil((_now - account.login_time) / 86400) > 9):# account will be expired soon, relogin here
    #             account.relogin()
    #     return accountPool


if __name__ == '__main__':
    Main(14)