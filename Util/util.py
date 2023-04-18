import time
import re
from selenium.webdriver.support import expected_conditions as EC
import requests
from hyper.contrib import HTTP20Adapter
# Constant = {
#     'domain': 'https://buff.163.com/', # buff domain
#     'ip_check_ab_addr': 'https://buff.163.com/', # the addr to check if ip works
#     'home_ab_dir': '/home/jerryin/jupyter_proj/csgo/', # the absolute root addr
#     'ip_pool_rel_dir': 'Ip/ipPool.pkl', # the relative file address compared to 'the absolute root addr'
#     'account_availability_check_rel_addr': 'api/market/goods?game=csgo&page_num=1&use_suggestion=0&_=' # the relative addr to check the account if available or not
# }
def getProxy(ip):
    return {"http": ip, "https": ip}

def getMilliTime():
    return str(round(time.time() * 1000))

class ConstantClass(object):
    def __init__(self):
        self.domain = 'https://buff.163.com' # buff domain
        self.ip_check_addr = 'https://buff.163.com' # the addr to check if ip works
        self.home_dir = '/home/jerryin/jupyter_proj/csgo/' # the root addr 
        self.ip_pool_dir = self.home_dir + 'Ip/ipPool.pkl' # the file address compared to 'the absolute root addr'
        self.account_pool_dir = self.home_dir + 'Account/accountPool.pkl' # the file address compared to 'the absolute root addr'
        
        self.account_availability_check_re_addr = '/api/market/goods?game=csgo&page_num=1&category=csgo_type_weaponcase&use_suggestion=0&_=' + getMilliTime()
        self.account_availability_check_ab_addr = self.domain +  self.account_availability_check_re_addr# the addr to check the account if available or not
        
        self.notification_without_timestamp_addr = '/api/message/notification?_=' # the url for notification without time stamp
        
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
        self.sessions = requests.session() # the session for accessing buff
        self.sessions.mount(self.domain, HTTP20Adapter())
        self.sessions.headers = self.buff_req_headers

    def getGoodsAddr(self, goods_id, timestamp):
        return '/api/market/goods/sell_order?game=csgo&goods_id=' + goods_id + '&page_num=1&sort_by=price.asc&mode=&allow_tradable_cooldown=1&_=' + timestamp

Constant = ConstantClass()

class WaitValueMatch(object):
    def __init__(self, locator, pattern):
        self.locator = locator
        self.pattern = re.compile(pattern)

    def __call__(self, driver):
        try:
            element_text = EC._find_element(driver, self.locator).get_attribute('value')
            print(EC._find_element(driver, self.locator))
            print(element_text)
            return self.pattern.search(element_text)
        except Exception as e:
            print(e)
            return False