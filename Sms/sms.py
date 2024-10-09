import sys
# sys.path.append("/home/jerryin/jupyter_proj/csgo/")
sys.path.append("../")

from Util.util import Constant
import requests

class Sms(object):
    def __init__(self):
        self.username = 'jerryin'
        self.password = 'jerryin'
        self.sms_token = '5ca1208912d842529cf19f5ab29cc5e7'
        self.key_word = '%E7%BD%91%E6%98%93' # url code for 网易
        self.login_addr = 'http://api.ejiema.com/zc/data.php?code=login&user=' + self.username + '&password=' + self.password
        self.sms_balance_addr = 'http://api.ejiema.com/zc/data.php?code=leftAmount&token=' + self.sms_token # the address get the balance of my account
        self.sms_phone_addr = 'http://api.ejiema.com/zc/data.php?code=getPhone&token=' + self.sms_token
        self.sms_message_addr = 'http://api.ejiema.com/zc/data.php?code=getMsg&token=' + self.sms_token
        self.sms_release_addr = 'http://api.ejiema.com/zc/data.php?code=release&token=' + self.sms_token
        self.sms_block_addr = 'http://api.ejiema.com/zc/data.php?code=block&token=' + self.sms_token
        self.sms_send_addr = 'http://api.ejiema.com/zc/data.php?code=send&token=' + self.sms_token
        
    def login(self):
        '''
        login to the sms platform and get the token

        return: 
            token: str
        '''
        return requests.get(self.login_addr).text
    
    def getBalance(self):
        '''
            return the accout balance. str
        '''

        return requests.get(self.sms_balance_addr).text

    def getPhone(self, phone = '', province = '', card_type = ''):
        '''
            phone: optional. 指定的号码，不填的话表示随机获取号码；(phone)
            province: optional. 省份，具体名称可参照APP里的；(province)
            card_type: optional. 选值范围：[实卡,虚卡,全部]。(cardType)
            
            return: phone number: str.
        '''
        phone_str = '' if phone == '' else '&phone=' + phone
        province_str = '' if province == '' else '&province=' + province
        card_type_str = '' if card_type == '' else '&cardType=' + card_type
        addr = self.sms_phone_addr + phone_str + province_str + card_type_str
        return requests.get(addr).text
    
    def getMsg(self, phone):
        '''
            return the message
            phone: compulsory. the phone number to get the sms.
            keyWord: compulsory. the keyWord of the message. here is 网易.

            return:
                success: the content of message.
                did not receive yet: return str contains '[尚未收到]'.
                fail: ERROR:'errror message'
        '''
        addr = self.sms_message_addr + '&phone=' + phone + '&keyWord=' + self.key_word
        return requests.get(addr).text
    
    def releasePhone(self, phone):
        '''
            release a defined phone number

            phone: compulsory. str.

            return: result of releasing. 
        '''
        addr = self.sms_release_addr + '&phone=' + phone
        return requests.get(addr).text

    def blockPhone(self, phone) -> str:
        '''
            block a defined phone number.
            phone: str. compulsory.

            return: result. str.
        '''
        addr = self.sms_block_addr + '&phone=' + phone
        return requests.get(addr).text
    
    def sendMsg(self, phone, toPhone, projId, content):
        '''
            send message from phone to toPhone.
            phone: str. compulsory. the send phone number.
            toPhone:  str. compulsory. the receiver.
            # projId: project id.
            content: the message content. （should be url coded）
            return: result.
        '''
        addr = self.sms_send_addr + '&phone=' + phone + '&toPhone=' + toPhone + '&content=' + content
        return requests.get(addr).text

sms = Sms()