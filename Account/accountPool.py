import sys
sys.path.append("/home/jerryin/jupyter_proj/csgo/")

from Util.util import Constant, getProxy
from Util import util
import time
import requests
import pickle
from Ip import ip
from Account.rawAccountPool import raw_accounts
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
from Sms.sms import sms
'''
    如果其他类来使用这个【账号池】类， 只需要指定账号池中需要的账号个数， 例如：account = AccountPool(3), 指定3个账号。
    这个类会先从磁盘中获取所有之前保存的账号(accountPool.pkl文件)，然后遍历磁盘中的账号池，留下有用的，删除没用的账号。
    如果留下的账号达到了需要的账号数，例3个，则直接返回AccountPool类，否则加入新的账号。
    新账号使用虚拟登录，手动登录。详见Account类的login方法。
'''
class AccountPool(object):
    '''
        methods:
        getAccountsFromDisk -> list: return accoount_list in the accountPool object which stored in a file
        updateAccountPool -> None: update all accounts in account_list (length of account_list is account_num)
        addNewAccounts -> None: append (account_num - len(account_list)) accounts in account_list
    '''
    def __init__(self, account_num: int) -> None:
        self.account_num = account_num
        self.account_list = []
        self.updateAccountPool(self.getAccountsFromDisk())
        self.addNewAccounts(self.account_num - len(self.account_list))
        self.account_num = account_num
        
    def __getitem__(self, index):
        '''
            example: ccount = AccountPool(3)  account[1] return the 2nd account in the account_list.
        '''
        return self.account_list[index]
    
    def __len__(self):
        '''
            example: account = AccountPool(3)  len(account) return 3.
        '''
        return len(self.account_list)

    def getAccountsFromDisk(self) -> list:
        '''
            return the AccountPool class stored in the disk, example: accountPool.pkl
        '''
        try:
            with open(Constant.account_pool_dir, 'rb') as fin: 
                account_list = pickle.load(fin).account_list
                print('the length of accounts stored in the disk is : ' + str(len(account_list)))
                return account_list
        except:
            print('open the account pool file failed')
            return []
            
    def updateAccountPool(self, account_list: list) -> None:
        '''
            update all accounts in the accountPool class, update to the login status.
        '''
        for index in range(0, len(account_list)):
            time.sleep(1)
            if index >= self.account_num: 
                '''
                    if the number of required accounts <= the number of all accounts in the account pool, return the first self.account_num accounts.
                    example: index = 5, self.account_num = 3, only return the first 3 accounts in the account list.
                '''
                self.account_list = account_list[:self.account_num]
                return 
            if not account_list[index].isIpAlive(): # if the ip is not alived, then update the ip.
                account_list[index].updateIp()
            status = account_list[index].accountStatus() # check the account login status.
            if status == 0: # this account is logined
                continue
            elif status == 1: # this account did not login
                if not account_list[index].login():
                    index -= 1
            else: # this account is been blocked or other problems
                account_list[index].blockPhone()
                # account_list[index].login()
                index -= 1
        
        self.account_list = account_list

    
    def addNewAccounts(self, account_num: int) -> None:
        '''
            add new accounts into the account pool.
        '''
        for index in range(0, account_num):
            account = Account()
            print('account status in addnewaccounts method: ' + str(account.status))
            if account.status >= 0: # if the account is logined, add this account into the pool, else index - 1 then get a new account.
                self.account_list.append(account)
            else:
                index -= 1

class Account(object):
    '''
        methods:
            isIpAlive -> bool: is ip alive
            blockPhone -> None: block the phone
            accountStatus -> int: 0: market available and login. 1: did not login. -1: market unavailable or other problems
            setCookieAndToken -> tuple: return cookie str and csrf_token str with csrf_token= substr
            updateIp -> None: update ip
            getIp -> str: return a new ip
            login -> None: login a new account.
    '''
    def __init__(self) -> None:
        self.ip = self.getIp()
        self.phone = ''
        self.login_time = 0
        self.cookie = ''
        self.csrf_token = ''
        self.status = -1
        while not self.login():
            continue
    
    def isIpAlive(self) -> bool:
        '''
            check the ip banded with the account is alive or not.
        '''
        return ip.checkIpAlive(self.ip.split('//')[1])

    def blockPhone(self) -> None:
        '''
            block the useless phone.
        '''
        print('block phone: ' + self.phone + ' block message is: ' + sms.blockPhone(self.phone))

    def accountStatus(self) -> int:
        '''
        return: 
            0: login and market available
            1: did not login
            -1: can not access market or other problems  
        '''
        headers = {
            ':method': 'GET',
            ':path': Constant.account_availability_check_re_addr,
            'cookie': self.cookie + 'csrf_token=' + self.csrf_token,
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        Constant.sessions.proxies = getProxy(self.ip)
        resp = Constant.sessions.get(Constant.account_availability_check_ab_addr, headers = headers)
        code = resp.json()['code']
        print('check account status, the code is: ' + code + '\n')
        if code == 'OK' or code == 'ok':
            return 0
        elif code == 'Login Required':
            return 1
        else:
            return -1
    
    def setCookieAndToken(self, cookieList: list) -> tuple: 
        '''
            process cookie map to cookie str and token str.
        '''
        cookie_map = cookieList
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

    def updateIp(self) -> None:
        '''
            update the ip banded with this account.
        '''
        self.ip = self.getIp()

    def getIp(self) -> str:
        return ip.getIp()
    
    def login(self) -> bool:
        '''
            login the new or expired account, return the bool type as success or not.
            process:
                1. open the page and click the login/register button.
                2. wait 1.5s to open the login iframe page.
                3. click 10 days no login and the agreement.
                4. get the phone number and input into the phone input box automatically.
                5. click the send sms button, and wait 5 sec for the HUMAN VERIFICATION. (DO IT BY SELF!!!)
                6. if did not receive the sms after 45 sec, block the phone number and return false.
                7. click the login button and wait maximum 30 sec to login and get the cookies.
                8. check the account status, return true if logined or vice vera.
        '''
        try:
            # proxy = Proxy({
            #     'proxyType': ProxyType.MANUAL,
            #     'httpProxy': self.ip,
            #     'sslProxy': self.ip,
            #     'noProxy': ''
            # })
            # options.proxy = proxy

            options =  webdriver.ChromeOptions()

            options.add_experimental_option("detach", True) # make the chrome window always opened
            
            
            while True: # get the useful ip
                options.add_argument(f"--proxy-server={self.ip}")
                driver = webdriver.Chrome(options = options)
                driver.get(Constant.ip_check_addr)
                try:
                    return_ip_addr = driver.find_element_by_tag_name('pre') # return 101.37.22.207
                    if return_ip_addr.text == self.ip:
                        print('IP ' + self.ip + 'can be use' + '\n')
                        driver.close()
                        break
                except BaseException as e:
                    driver.close()
                    options.arguments.remove(f"--proxy-server={self.ip}")
                    self.updateIp()
                    continue
            
            
            driver = webdriver.Chrome(options = options)

            driver.get(Constant.domain)
            try:
                driver.find_element_by_xpath('//div[@class="nav nav_entries"]/ul/li/a[@onclick="loginModule.showLogin()"]').click() # click login/register button
            except BaseException as e:
                return False
            time.sleep(1.5) # after clicking the login/register button, wait 2 sec to load login iframe page

            try:
                driver.find_element_by_xpath('//div[@id="remember-me"]/span/i').click() # click 10 days no login
                driver.find_element_by_xpath('//div[@id="agree-checkbox"]/span/i').click() # click agreement
            except BaseException as e:
                return False
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="j_login"]/iframe')))
                driver.switch_to.frame(driver.find_element_by_xpath('//div[@id="j_login"]/iframe')) # swith to the login iframe
            except BaseException as e:
                return False
            code = []
            while(len(code) == 0): # did not receive the code verification
                self.phone = sms.getPhone() # get a new phone number
                # self.phone = '16537928820'
                print('buff phone number: ' + self.phone)
                try:
                    driver.find_element_by_xpath('//input[@class="dlemail j-nameforslide"]').send_keys(self.phone) 
                except BaseException as e:
                    return  False
                time.sleep(5) # time sleep for the human verification
                try:
                    driver.find_element_by_xpath('//div[@class="pcbtn f-fl"]/a').click() # send the sms code
                except BaseException as e:
                    return False
                _ind = 0
                while(_ind <= 15): # wait 45 sec fro receiving the code
                    time.sleep(3) # every iteration waiting 3 sec

                    code = re.findall(r"验证码：(\d+)，", sms.getMsg(self.phone))
                    # code = ['883568']
                    if(len(code) > 0): # if receive the code 
                        try:
                            driver.find_element_by_xpath('//input[@class="j-inputtext pcin"]').send_keys(code[0]) # input the code
                        except BaseException as e:
                            return False
                        break
                    _ind += 1
                # WebDriverWait(driver, 100).until(WaitValueMatch((By.CLASS_NAME, 'j-inputtext'), r'[0-9]+'))
                if(_ind > 15): # did not receive the code after 120 sec
                    self.blockPhone()
                    return False
                # time.sleep(1) #sleep for clicking the login button
                try:
                    driver.find_element_by_xpath('//div[@class="f-cb loginbox"]/a').click()
                except BaseException as e:
                    return False
            try:
                driver.switch_to.default_content()
            
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'go_to_steam'))) # wait maxmium 30 sec to login and get the cookie
            except BaseException as e:
                print('did not find go to steam button after login, account phone is ' + self.phone + ': ' + e + '\n')
                return False
            
            self.login_time = time.time()
            self.cookie, self.csrf_token = self.setCookieAndToken(driver.get_cookies())
            self.status = self.accountStatus()
            
            if self.status < 0:
                self.blockPhone()
                return False
            return True
        except BaseException as e:
            print('login exception: ' + e)
            return False

if __name__ == '__main__':
    AccountPool(1)
# class AccountPool(object):
#     def __init__(self):
#         self.raw_accounts = raw_accounts
#         self.ipPool = self.getSavedIpPool()
#         self.accountPool = self.setAccountPool()
#         self.saveIpAccountPool()

#     def __getitem__(self, index):
#         return self.accountPool[index]
    
#     def __len__(self):
#         return len(self.accountPool)

#     def saveIpAccountPool(self): # save the array into a file called ipPool.pkl
#         with open(Constant.ip_pool_dir, 'wb') as fout:
#             pickle.dump(self.ipPool, fout, pickle.HIGHEST_PROTOCOL)
        
#         with open(Constant.account_pool_dir, 'wb') as fout:
#             pickle.dump(self.accountPool, fout, pickle.HIGHEST_PROTOCOL)

#     def setAccountPool(self):
#         ip_len = len(self.ipPool)
#         acc_len = len(raw_accounts)
#         print('account len: ' + str(acc_len))
#         print('ip len: ' + str(ip_len))
#         if ip_len <= acc_len:
#             print('ip len is less then account len')
        
#         acc_ind = 0
#         accountPool = []
#         for ip_ind in range(0, ip_len):
#             if(acc_ind >= acc_len):
#                 break

#             _ip = self.ipPool[0]
#             accountPool.append(Account(_ip, raw_accounts[acc_ind]))
#             self.ipPool.remove(self.ipPool[0])
#             acc_ind += 1
#         return accountPool
    
#     def getCurrentIpPool(self): # get real-time ip pool (cost time to test all ip addr if alive or not)
#         return IpPool()

#     def getSavedIpPool(self): # get ip pool from a file (stored before)
#         with open(Constant.ip_pool_dir, 'rb') as fin: 
#             return pickle.load(fin)

# class Account(object):
#     def __init__(self, ipObj, raw_account):
#         self.ipObj = ipObj
#         self.buff_phone = raw_account['buff_phone']
#         self.buff_pwd = raw_account['buff_pwd']
#         self.steam_email = raw_account['steam_email']
#         self.steam_account = raw_account['steam_account']
#         self.steam_pwd = raw_account['steam_pwd']
#         self.login_time = 0
#         self.cookie, self.csrf_token = self.setCookieAndToken()
#         self.is_login, self.is_market = self.checkLoginAndMarket()
#         # self.is_market = self.isMarketAvailable()
    
#     def relogin(self):
#         self.cookie, self.csrf_token = self.setCookieAndToken()
#         self.is_login, self.is_market = self.checkLoginAndMarket()


#     def setCookieAndToken(self): # process cookie map to cookie str and token str
#         cookie_map = self.getCookie()
#         cookie = ''
#         deviceId = ''
#         LocaleSupported = ''
#         game = ''
#         NTES_YD_SESS = ''
#         S_INFO = ''
#         P_INFO = ''
#         remember_me = ''
#         session = ''
#         csrf_token = ''
#         for _map in cookie_map:
#             if(_map['name'] == 'csrf_token'):
#                 csrf_token = _map['value']
#             elif(_map['name'] == 'Device-Id'):
#                 deviceId = 'Device-Id=' + _map['value'] + '; '
#             elif(_map['name'] == 'Locale-Supported'):
#                 LocaleSupported = 'Locale-Supported=' + _map['value'] + '; '
#             elif(_map['name'] == 'game'):
#                 game = 'game=' + _map['value'] + '; '
#             elif(_map['name'] == 'NTES_YD_SESS'):
#                 NTES_YD_SESS = 'NTES_YD_SESS=' + _map['value'] + '; '
#             elif(_map['name'] == 'S_INFO'):
#                 S_INFO ='S_INFO=' + _map['value'] + '; '
#             elif(_map['name'] == 'P_INFO'):
#                 P_INFO = 'P_INFO=' + _map['value'] + '; '
#             elif(_map['name'] == 'remember_me'):
#                 remember_me = 'remember_me=' + _map['value'] + '; '
#             elif(_map['name'] == 'session'):
#                 session = 'session=' + _map['value'] + '; '
#         cookie = deviceId + LocaleSupported + game + NTES_YD_SESS + S_INFO + P_INFO + remember_me + session
#         return cookie, csrf_token
    
#     def getCookie(self): # get cookies stored in the chrome
#         proxy = Proxy({
#             'proxyType': ProxyType.MANUAL,
#             'httpProxy': self.ipObj.ip,
#             'sslProxy': self.ipObj.ip,
#             'noProxy': ''
#         })

#         options =  webdriver.ChromeOptions()
#         options.proxy = proxy
#         options.add_experimental_option("detach", True) # make the chrome window always opened
#         driver = webdriver.Chrome(options = options)
        
        
#         driver.get(Constant.domain)

#         driver.find_element_by_xpath('//div[@class="nav nav_entries"]/ul/li/a[@onclick="loginModule.showLogin()"]').click() # click login/register button
#         time.sleep(2) # after clicking the login/register button, wait 2 sec to load login iframe page

        
#         driver.find_element_by_xpath('//div[@id="remember-me"]/span/i').click() # click 10 days no login
#         driver.find_element_by_xpath('//div[@id="agree-checkbox"]/span/i').click() # click agreement
        
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="j_login"]/iframe')))
#         driver.switch_to.frame(driver.find_element_by_xpath('//div[@id="j_login"]/iframe')) # swith to the login iframe
        
#         driver.find_element_by_id('phoneipt').send_keys(self.buff_phone) # input phone number

#         if self.buff_pwd != '': # if has buff password
#             driver.find_element_by_xpath('//a[@class="tab0"]').click() # click 'using password login' button
#             driver.find_element_by_xpath('//input[@class="j-inputtext dlemail"]').send_keys(self.buff_pwd) 
            
#             time.sleep(5) # time sleep for a human drag the progress （human verification）
#             driver.find_element_by_id('submitBtn').click()
#         else: # using sms api to get the code
#             sms = Sms()
#             code = []
#             while(len(code) == 0): # did not receive the code verification
#                 self.buff_phone = sms.getPhone() # get a new phone number
#                 # self.buff_phone = '16537928820'
#                 print('buff phone number: ' + self.buff_phone)
#                 driver.find_element_by_xpath('//input[@class="dlemail j-nameforslide"]').send_keys(self.buff_phone) 
#                 time.sleep(5) # time sleep for the human verification
#                 driver.find_element_by_xpath('//a[@class="tabfocus getsmscode "]').click() # send the sms code
#                 _ind = 0
#                 while(_ind <= 40): # wait 120 sec fro receiving the code
#                     time.sleep(3) # every iteration waiting 3 sec

#                     code = re.findall(r"验证码：(\d+)，", sms.getMsg(self.buff_phone))
#                     # code = ['883568']
#                     if(len(code) > 0): # if receive the code 
#                         driver.find_element_by_xpath('//input[@class="j-inputtext pcin"]').send_keys(code[0]) # input the code
#                         break
#                     _ind += 1
#                 # WebDriverWait(driver, 100).until(WaitValueMatch((By.CLASS_NAME, 'j-inputtext'), r'[0-9]+'))
#                 if(_ind > 40): # did not receive the code after 120 sec
#                     sms.blockPhone(self.buff_phone)
            
#             time.sleep(3) #sleep for clicking the login button
#             driver.find_element_by_xpath('//div[@class="f-cb loginbox"]/a').click()
#         driver.switch_to.default_content()
#         WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'go_to_steam'))) # wait maxmium 30 sec to login and get the cookie
        
#         self.login_time = time.time()
#         return driver.get_cookies()
    

#     # def isMarketAvailable(self): # check if this account can access market
#     #     if self.is_login == False:
#     #         return False
#     #     return self.checkLoginAndMarket(False)
    
#     # def isLogin(self): # check if this account login
#     #     return self.checkLoginAndMarket(True)
    
#     def checkLoginAndMarket(self): # check if this account login or can access market
#         headers = {
#             ':method': 'GET',
#             ':path': Constant.account_availability_check_re_addr,
#             'cookie': self.cookie + 'csrf_token=' + self.csrf_token,
#             'sec-fetch-user': '?1',
#             'upgrade-insecure-requests': '1',
#         }
#         resp = Constant.sessions.get(Constant.account_availability_check_ab_addr, headers = headers, proxies = self.ipObj.proxies)
#         code = resp.json()['code']
#         print(code)
#         if code == 'OK' or code == 'ok':
#             return True, True
#         elif code == 'Login Required':
#             return False, False
#         elif code == 'Action Forbidden':
#             return True, False
#         else:
#             return False, False

# if __name__ == '__main__':
#     AccountPool()