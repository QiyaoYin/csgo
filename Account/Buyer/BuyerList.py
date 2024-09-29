import sys
sys.path.append("/home/jerryin/jupyter_proj/csgo/")

import pandas as pd
from Util.util import Constant

class Buyers(object):
    '''
        从newAccount.csv中读取数据，保存在buyerlist.csv和disabledbuyerlist.csv中
        methods:
            addNewAccount: add new accounts to buyerlist.csv and remove the accounts from newAccount.csv.
            removeNewAccount: remove accounts from newAccount.csv.
            saveBuyerList: save buyerlist to buyerlist.csv.
            saveDisabledBuyerList: save disabledBuyerList instance to disabledBuyerList.csv.
            buyerlistToJson: change dataframe buyerlist to json type.
            pdToJson: pandas dataframe to json.
            disabledBuyerListToJson: change dataframe disabledBuyerList to json type.
            update: pass.
            disableAccount: remove disabled account from buyerlist to disabledbuyerlist.
    '''
    def __init__(self) -> None:
        self.buyerList = pd.read_csv(Constant.buyer_list_dir, header = 0)
        
        self.disabledBuyerList = pd.read_csv(Constant.disabled_buyer_list_dir, header = 0)

        self.newAccountList = pd.read_csv(Constant.new_account_list_dir, header = 0)
        
        self.addNewAccount()
        
        self.buyerListJson = self.pdToJson(self.buyerList)

        self.disabledBuyerListJson = self.pdToJson(self.disabledBuyerList)

    def addNewAccount(self) -> None:
        '''
            add new accounts to buyerlist.csv and remove the accounts from newAccount.csv.
        '''
        self.buyerList = pd.concat([self.buyerList,self.newAccountList], ignore_index=True)
        self.removeNewAccount()
        self.saveBuyerList()

    def removeNewAccount(self) -> None:
        '''
            remove accounts from newAccount.csv.
        '''
        self.newAccountList.drop(self.newAccountList.index[:len(self.newAccountList)], inplace = True)
        
        self.newAccountList.to_csv(Constant.new_account_list_dir, index = False)
    
    def update(self) -> None:
        pass
    
    def saveBuyerList(self) -> None:
       '''
            save buyerlist to buyerlist.csv.
       '''
       self.buyerList.to_csv(Constant.buyer_list_dir, index = False)
    
    def saveDisabledBuyerList(self) -> None:
        '''
            save disabledBuyerList instance to disabledBuyerList.csv.
        '''
        self.disabledBuyerList.to_csv(Constant.disabled_buyer_list_dir, index = False)
    
    def pdToJson(self, pd) -> list:
        '''
            pandas dataframe to json.
        '''
        res = []
        for _, df_gp in pd.groupby('BUFF_ACCOUNT'):
            res.append(df_gp.to_dict(orient='records')[0])
        return res
    
    def buyerListToJson(self) -> list:
        '''
            change dataframe buyerlist to json type.
        '''
        return self.pdToJson(self.buyerList)
        
    def disabledBuyerListToJson(self) -> list:
        '''
            change dataframe disabledBuyerList to json type.
        '''
        return self.pdToJson(self.disabledBuyerList)
        
    def disableAccount(self, buff_phone) -> list:
        '''
            remove disabled account from buyerlist to disabledbuyerlist.
        '''
        _index = self.buyerList[self.buyerList['BUFF_ACCOUNT'] == int(buff_phone)].index
        disabled_account = self.buyerList.iloc[_index]
        
        self.disabledBuyerList = self.disabledBuyerList.append(disabled_account, ignore_index = True)
        
        self.buyerList.drop(_index, inplace = True)

        self.saveBuyerList()
        self.saveDisabledBuyerList()

        self.buyerListJson = self.buyerListToJson()
        self.disabledBuyerListJson = self.disabledBuyerListToJson()

        return self.buyerListJson
    

if __name__ == '__main__':
    buyer = Buyers()