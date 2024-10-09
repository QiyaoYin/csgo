import sys
# sys.path.append("/home/jerryin/jupyter_proj/csgo/")
sys.path.append("../")

import time
import requests
from hyper.contrib import HTTP20Adapter
import json
# import kdl
# Constant = {
#     'domain': 'https://buff.163.com/', # buff domain
#     'ip_check_ab_addr': 'https://buff.163.com/', # the addr to check if ip works
#     'home_ab_dir': '/home/jerryin/jupyter_proj/csgo/', # the absolute root addr
#     'ip_pool_rel_dir': 'Ip/ipPool.pkl', # the relative file address compared to 'the absolute root addr'
#     'account_availability_check_rel_addr': 'api/market/goods?game=csgo&page_num=1&use_suggestion=0&_=' # the relative addr to check the account if available or not
# }

class ConstantClass(object):
    def __init__(self):
        # self.ip_check_addr

        self.domain = 'https://buff.163.com' # buff domain
        self.ip_check_addr = 'https://icanhazip.com/' # the addr to check if ip works
        # self.home_dir = '/home/jerryin/jupyter_proj/csgo/' # the root addr 
        self.home_dir = '../' # the root addr 
        self.ip_pool_dir = self.home_dir + 'Ip/ipPool.pkl' # the file address compared to 'the absolute root addr'
        self.account_pool_dir = self.home_dir + 'Account/accountPool.pkl' # the file address compared to 'the absolute root addr'
        self.all_buyers_dir = self.home_dir + 'Account/Buyer/allBuyers.pkl' # the file is an instance, stored all buyer accounts.
        self.buyer_list_dir = self.home_dir + 'Account/Buyer/List/buyerList.csv' # the csv stored all useful buyer account info.
        self.disabled_buyer_list_dir = self.home_dir + 'Account/Buyer/List/disabledBuyerList.csv' # the csv stored all disabled buyer account info.
        self.new_account_list_dir = self.home_dir + 'Account/Buyer/List/newAccount.csv' # the csv stored new account which does not used.

        self.account_availability_check_re_addr = '/api/market/goods?game=csgo&page_num=1&category=csgo_type_weaponcase&use_suggestion=0&_=' + self.getMilliTime()
        self.account_availability_check_ab_addr = self.domain +  self.account_availability_check_re_addr # the addr to check the account if available or not
        
        self.notification_without_timestamp_addr = '/api/message/notification?_=' # the url for notification without time stamp
        self.buy_goods_ab_addr = '/api/market/goods/buy' # the url for buying goods
        self.buy_goods_re_addr = self.domain + self.buy_goods_ab_addr
        self.game = 'csgo'
        self.payment_method = '3'

        self.buyer_cookie = 'Device-Id=xsTUySJ9cGu53kLrQSZ1; Locale-Supported=en; game=csgo; AQ_HD=1; YD_SC_SID=648A3875183F4E35BD18091330D767F0; NTES_YD_SESS=t7bms.vYLhVvaCFN32skR8TaYUCRXw_gT5R1p9JEpcN8uWdmu57zsxdQ4WMWvoFjhvoXl_9V9s9Vi3sUTUg5moN4uWCrtwRJ_UxWlTwyUeEwttUVwT84exPUo6snngfb_F8ttoJJLrE7xt1G5ie4bX1yqs2YjdN1k7Nz9Vq0eVU7PZOtWvnNxCjbSB6oLqvMVXWsccZsYgCPammAFQ3U2oaC8ahLgSHpSGHXMhhSCfM8b; S_INFO=1681823795|0|0&60##|17376591844; P_INFO=17376591844|1681823795|1|netease_buff|00&99|zhj&1681698222&netease_buff#zhj&330200#10#0#0|&0|null|17376591844; remember_me=U1106621510|9y79AjHgZ1VIOsP1dKK3uSq8uF6AIHKq; session=1-YWigjRpBmN4glrD9-skbnQqFVoUMbIIXMe3_xLf3vOEm2033920798; '
        self.buyer_csrf_token = 'ImVlODc4M2Q0ZTlkMmM1NTAwZmFjM2UxMDY5MzRjOWUxOGVlNTJmNjci.FyApuw.feJ5IC1o7_5ZCqCBDPL6OOAULes'
        self.dingding_mesasge_addr = "https://oapi.dingtalk.com/robot/send?access_token=35a63d6aae0234ee0e794b7f6cec9ec06a44cd89f42c6d9d336488730494f50c"
        
        self.buff_req_headers = { # request header for accessing market in buff
            ':authority': 'buff.163.com',
            ':scheme': 'https',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mod': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
    
        # self.sessions = requests.session() # the session for accessing buff
        # self.sessions.mount(self.domain, HTTP20Adapter())
        # self.sessions.headers = self.buff_req_headers

        # self.auth = kdl.Auth("o81ooetpm0jqbtoauegq", "rc4cbfb9wslxolylje30wgj0q8yqzngz")
        # self.client = kdl.Client(self.auth, timeout=(8, 12), max_retries=3)
        # https://github.com/kuaidaili/python-sdk/tree/master/api-sdk
        
        # self.goods_id = '45237'
        # 命悬一线武器箱: 45237
        self.goods = {'id': '45237', 'bar': 7.6}
    def getGoodsAddr(self, goods_id, timestamp) -> str:
        return '/api/market/goods/sell_order?game=csgo&goods_id=' + goods_id + '&page_num=1&sort_by=price.asc&mode=&allow_tradable_cooldown=1&_=' + timestamp

    def getSession(self) -> object:
        session = requests.session()
        session.mount(self.domain, HTTP20Adapter())
        session.headers = self.buff_req_headers
        return session
    
    def getProxy(self,ip) -> dict:
        return {"http": "http://" + ip, "https": "http://" + ip}

    def checkAlive(self, proxies) -> tuple: # check if ip alive or dead
        try:
            current_time = time.time()
            resp = requests.get(self.ip_check_addr, proxies)
            lag = time.time() - current_time
            # print(resp.status_code)
            return (True, lag) if resp.status_code == 200 else (False, -1)
        except:
            return (False, -1)

    def getMilliTime(self) -> str:
        return str(round(time.time() * 1000))


Constant = ConstantClass()
# class WaitValueMatch(object):
#     def __init__(self, locator, pattern):
#         self.locator = locator
#         self.pattern = re.compile(pattern)

#     def __call__(self, driver):
#         try:
#             element_text = EC._find_element(driver, self.locator).get_attribute('value')
#             print(EC._find_element(driver, self.locator))
#             print(element_text)
#             return self.pattern.search(element_text)
#         except Exception as e:
#             print(e)
#             return False


class BuyerAccount(object):
    def __init__(self, csrf_token):
        self.allow_tradable_cooldown = '0'
        self.token = ''
        self.cdkey_id = ''
        self.cookie = Constant.buyer_cookie
        self.csrf_token = self.notification(csrf_token).headers.get(b'set-cookie').decode("utf-8").split(';')[0].split('=')[1]

    def notification(self, csrf_token):
        _path = Constant.notification_without_timestamp_addr + Constant.getMilliTime()
        _url = Constant.domain + _path
        _header = {
            ':method': 'GET',
            ':path': _path,
            'cookie': self.cookie + 'csrf_token=' + csrf_token,
            'referer': Constant.domain + '/?game=csgo'
        }
        return Constant.getSession().get(_url, headers = _header)
        
    def buy_goods(self, goods_id, sell_order_id, price):
        _header = {
            ':method': 'POST',
            ':path': Constant.buy_goods_ab_addr,
            'referer': Constant.domain + '/goods/' + goods_id,
            'content-type': 'application/json',
            'origin': Constant.domain,
            'cookie': self.cookie + 'csrf_token=' + self.csrf_token,
            'x-csrftoken': self.csrf_token
        }

        form_data = {
            "game": Constant.game,
            "goods_id": goods_id,
            "sell_order_id": sell_order_id,
            "price": price,
            "pay_method": Constant.payment_method,
            "allow_tradable_cooldown": self.allow_tradable_cooldown,
            "token": self.token,
            "cdkey_id":self.cdkey_id
        }

        resp = Constant.sessions.post(Constant.buy_goods_re_addr, headers = _header, json = form_data)
        self.csrf_token = self.notification(self.csrf_token).headers.get(b'set-cookie').decode("utf-8").split(';')[0].split('=')[1]
        return resp.json()
    
    def sendMessage(self, price, message = 'jerryin add a new good in buff, price is '):
        headers = {'Content-Type':'application/json'}
        data = {"msgtype":"text","text":{ "content": message + price}}
        requests.post(Constant.dingding_mesasge_addr, data = json.dumps(data), headers = headers)

Buyer = BuyerAccount(Constant.buyer_csrf_token)