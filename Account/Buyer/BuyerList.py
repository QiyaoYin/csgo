import sys
sys.path.append("/home/jerryin/jupyter_proj/csgo/")

import pandas as pd
from Util.util import Constant
'''
这个类的作用是保存最新可用的buyer账号和不可用的buyer账号。
若在过程中发现某个buyer账号不可用，则需调用diableAccount方法来更新。
'''
class BuyerList(object):
    '''
        buyer = Buyer()会做以下动作：
            1. 读取newAccount.csv中的所有新账号，保存至buyerlist.csv中并删除newAccount.csv中的所有新账号。
            2. buyer：存放所有购买账号的信息（BUFF_ACCOUNT,BUFF_PWD,STEAM_EMAIL,STEAM_ACCOUNT,STEAM_PWD）, pandas的dataframe类型。
            3. disabledBuyer: 存放所有无用的购买账号的信息，pandas的dataframe类型。
            4. buyerList: buyer的List形式，与buyer同步更新。
            5. disabledBuyerList： 同上。
        methods:
            addNewAccount: add new accounts to buyerlist.csv and remove the accounts from newAccount.csv.
            removeNewAccount: remove accounts from newAccount.csv.
            saveBuyerList: save buyerlist to buyerlist.csv.
            saveDisabledBuyerList: save disabledBuyerList instance to disabledBuyerList.csv.
            buyerToDict: change dataframe buyerlist to json type.
            pdToDict: pandas dataframe to dict.
            disabledBuyerToDict: change dataframe disabledBuyerList to json type.
            update: pass.
            disableAccount: remove disabled account from buyerlist to disabledbuyerlist, return new buyerList.
    '''
    def __init__(self) -> None:
        self.buyer = pd.read_csv(Constant.buyer_list_dir, header = 0)
        
        self.disabledBuyer = pd.read_csv(Constant.disabled_buyer_list_dir, header = 0)

        self.newAccount = pd.read_csv(Constant.new_account_list_dir, header = 0)
        
        self.addNewAccount()
        
        self.buyerList = self.pdToDict(self.buyer)

        self.disabledBuyerList = self.pdToDict(self.disabledBuyer)

    def addNewAccount(self) -> None:
        '''
            add new accounts to buyerlist.csv and remove the accounts from newAccount.csv.
        '''
        self.buyer = pd.concat([self.buyer,self.newAccount], ignore_index=True)
        self.removeNewAccount()
        self.saveBuyerList()

    def removeNewAccount(self) -> None:
        '''
            remove accounts from newAccount.csv.
        '''
        self.newAccount.drop(self.newAccount.index[:len(self.newAccount)], inplace = True)
        
        self.newAccount.to_csv(Constant.new_account_list_dir, index = False)
    
    def update(self) -> None:
        pass
    
    def saveBuyerList(self) -> None:
       '''
            save buyerlist to buyerlist.csv.
       '''
       self.buyer.to_csv(Constant.buyer_list_dir, index = False)
    
    def saveDisabledBuyerList(self) -> None:
        '''
            save disabledBuyerList instance to disabledBuyerList.csv.
        '''
        self.disabledBuyer.to_csv(Constant.disabled_buyer_list_dir, index = False)
    
    def pdToDict(self, pd) -> dict:
        '''
            pandas dataframe to json.
        '''
        res = {}
        for key, df_gp in pd.groupby('BUFF_ACCOUNT'):
            res[key] = df_gp.to_dict(orient='records')[0]
        return res
    
    def buyerToDict(self) -> dict:
        '''
            change dataframe buyerlist to json type.
        '''
        return self.pdToDict(self.buyer)
        
    def disabledBuyerToDict(self) -> dict:
        '''
            change dataframe disabledBuyerList to json type.
        '''
        return self.pdToDict(self.disabledBuyer)
        
    def disableAccount(self, buff_phone) -> list:
        '''
            remove disabled account from buyerlist to disabledbuyerlist.
        '''
        _index = self.buyer[self.buyer['BUFF_ACCOUNT'] == int(buff_phone)].index
        disabled_account = self.buyer.iloc[_index]
        
        self.disabledBuyer = self.disabledBuyer.append(disabled_account, ignore_index = True)
        
        self.buyer.drop(_index, inplace = True)

        self.saveBuyerList()
        self.saveDisabledBuyerList()

        self.buyerList = self.buyerToDict()
        self.disabledBuyerList = self.disabledBuyerToDict()

        return self.buyerList
    


buyerlist = BuyerList()