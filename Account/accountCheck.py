import sys
sys.path.append("/home/jerryin/jupyter_proj/csgo/")

from Util.util import Constant
from Util import util
import time
import requests
import pickle
from Ip.ipCheck import IpPool, Ip
from Account.rawAccountPool import raw_accounts
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Sms.sms import Sms
import re

class AccountPool(object):
    def __init__(self):
        self.raw_accounts = raw_accounts
        self.ipPool = self.getSavedIpPool()
        self.accountPool = self.setAccountPool()
        self.saveIpAccountPool()

    def __getitem__(self, index):
        return self.accountPool[index]
    
    def __len__(self):
        return len(self.accountPool)

    def saveIpAccountPool(self): # save the array into a file called ipPool.pkl
        with open(Constant.ip_pool_dir, 'wb') as fout:
            pickle.dump(self.ipPool, fout, pickle.HIGHEST_PROTOCOL)
        
        with open(Constant.account_pool_dir, 'wb') as fout:
            pickle.dump(self.accountPool, fout, pickle.HIGHEST_PROTOCOL)

    def setAccountPool(self):
        ip_len = len(self.ipPool)
        acc_len = len(raw_accounts)
        print('account len: ' + str(acc_len))
        print('ip len: ' + str(ip_len))
        if ip_len <= acc_len:
            print('ip len is less then account len')
        
        acc_ind = 0
        accountPool = []
        for ip_ind in range(0, ip_len):
            if(acc_ind >= acc_len):
                break

            _ip = self.ipPool[0]
            accountPool.append(Account(_ip, raw_accounts[acc_ind]))
            self.ipPool.remove(self.ipPool[0])
            acc_ind += 1
        return accountPool
    
    def getCurrentIpPool(self): # get real-time ip pool (cost time to test all ip addr if alive or not)
        return IpPool()

    def getSavedIpPool(self): # get ip pool from a file (stored before)
        with open(Constant.ip_pool_dir, 'rb') as fin: 
            return pickle.load(fin)

class Account(object):
    def __init__(self, ipObj, raw_account):
        self.ipObj = ipObj
        self.buff_phone = raw_account['buff_phone']
        self.buff_pwd = raw_account['buff_pwd']
        self.steam_email = raw_account['steam_email']
        self.steam_account = raw_account['steam_account']
        self.steam_pwd = raw_account['steam_pwd']
        self.login_time = 0
        self.cookie, self.csrf_token = self.setCookieAndToken()
        self.is_login, self.is_market = self.checkLoginAndMarket()
        # self.is_market = self.isMarketAvailable()
    
    def relogin(self):
        self.cookie, self.csrf_token = self.setCookieAndToken()
        self.is_login, self.is_market = self.checkLoginAndMarket()


    def setCookieAndToken(self): # process cookie map to cookie str and token str
        cookie_map = self.getCookie()
        cookie = ''
        deviceId = ''
        LocaleSupported = ''
        game = ''
        NTES_YD_SESS = ''
        S_INFO = ''
        P_INFO = ''
        remember_me = ''
        session = ''
        csrf_token = ''
        for _map in cookie_map:
            if(_map['name'] == 'csrf_token'):
                csrf_token = _map['value']
            elif(_map['name'] == 'Device-Id'):
                deviceId = 'Device-Id=' + _map['value'] + '; '
            elif(_map['name'] == 'Locale-Supported'):
                LocaleSupported = 'Locale-Supported=' + _map['value'] + '; '
            elif(_map['name'] == 'game'):
                game = 'game=' + _map['value'] + '; '
            elif(_map['name'] == 'NTES_YD_SESS'):
                NTES_YD_SESS = 'NTES_YD_SESS=' + _map['value'] + '; '
            elif(_map['name'] == 'S_INFO'):
                S_INFO ='S_INFO=' + _map['value'] + '; '
            elif(_map['name'] == 'P_INFO'):
                P_INFO = 'P_INFO=' + _map['value'] + '; '
            elif(_map['name'] == 'remember_me'):
                remember_me = 'remember_me=' + _map['value'] + '; '
            elif(_map['name'] == 'session'):
                session = 'session=' + _map['value'] + '; '
        cookie = deviceId + LocaleSupported + game + NTES_YD_SESS + S_INFO + P_INFO + remember_me + session
        return cookie, csrf_token
    
    def getCookie(self): # get cookies stored in the chrome
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': self.ipObj.ip,
            'sslProxy': self.ipObj.ip,
            'noProxy': ''
        })

        options =  webdriver.ChromeOptions()
        options.proxy = proxy
        options.add_experimental_option("detach", True) # make the chrome window always opened
        driver = webdriver.Chrome(options = options)
        
        
        driver.get(Constant.domain)

        driver.find_element_by_xpath('//div[@class="nav nav_entries"]/ul/li/a[@onclick="loginModule.showLogin()"]').click() # click login/register button
        time.sleep(2) # after clicking the login/register button, wait 2 sec to load login iframe page

        
        driver.find_element_by_xpath('//div[@id="remember-me"]/span/i').click() # click 10 days no login
        driver.find_element_by_xpath('//div[@id="agree-checkbox"]/span/i').click() # click agreement
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="j_login"]/iframe')))
        driver.switch_to.frame(driver.find_element_by_xpath('//div[@id="j_login"]/iframe')) # swith to the login iframe
        
        driver.find_element_by_id('phoneipt').send_keys(self.buff_phone) # input phone number

        if self.buff_pwd != '': # if has buff password
            driver.find_element_by_xpath('//a[@class="tab0"]').click() # click 'using password login' button
            driver.find_element_by_xpath('//input[@class="j-inputtext dlemail"]').send_keys(self.buff_pwd) 
            
            time.sleep(5) # time sleep for a human drag the progress （human verification）
            driver.find_element_by_id('submitBtn').click()
        else: # using sms api to get the code
            sms = Sms()
            code = []
            while(len(code) == 0): # did not receive the code verification
                self.buff_phone = sms.getPhone() # get a new phone number
                # self.buff_phone = '16537928820'
                print('buff phone number: ' + self.buff_phone)
                driver.find_element_by_xpath('//input[@class="dlemail j-nameforslide"]').send_keys(self.buff_phone) 
                time.sleep(5) # time sleep for the human verification
                driver.find_element_by_xpath('//a[@class="tabfocus getsmscode "]').click() # send the sms code
                _ind = 0
                while(_ind <= 40): # wait 120 sec fro receiving the code
                    time.sleep(3) # every iteration waiting 3 sec

                    code = re.findall(r"验证码：(\d+)，", sms.getMsg(self.buff_phone))
                    # code = ['883568']
                    if(len(code) > 0): # if receive the code 
                        driver.find_element_by_xpath('//input[@class="j-inputtext pcin"]').send_keys(code[0]) # input the code
                        break
                    _ind += 1
                # WebDriverWait(driver, 100).until(WaitValueMatch((By.CLASS_NAME, 'j-inputtext'), r'[0-9]+'))
                if(_ind > 40): # did not receive the code after 120 sec
                    sms.blockPhone(self.buff_phone)
            
            time.sleep(3) #sleep for clicking the login button
            driver.find_element_by_xpath('//div[@class="f-cb loginbox"]/a').click()
        driver.switch_to.default_content()
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'go_to_steam'))) # wait maxmium 30 sec to login and get the cookie
        
        self.login_time = time.time()
        return driver.get_cookies()
    

    # def isMarketAvailable(self): # check if this account can access market
    #     if self.is_login == False:
    #         return False
    #     return self.checkLoginAndMarket(False)
    
    # def isLogin(self): # check if this account login
    #     return self.checkLoginAndMarket(True)
    
    def checkLoginAndMarket(self): # check if this account login or can access market
        headers = {
            ':method': 'GET',
            ':path': Constant.account_availability_check_re_addr,
            'cookie': self.cookie + 'csrf_token=' + self.csrf_token,
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        resp = Constant.sessions.get(Constant.account_availability_check_ab_addr, headers = headers, proxies = self.ipObj.proxies)
        code = resp.json()['code']
        print(code)
        if code == 'OK' or code == 'ok':
            return True, True
        elif code == 'Login Required':
            return False, False
        elif code == 'Action Forbidden':
            return True, False
        else:
            return False, False

if __name__ == '__main__':
    AccountPool()