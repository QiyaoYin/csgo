# csgo repository

1. ip (no class): 
   1. getIps(num: int) -> ips: array
   2. checkAlive(ips) -> dict (ip: True or False) (using client.check_dps_valid(ips))
2. account: (class: AccountPool(num) -> the account pool contains num accounts)
   1. check the account every time at the begining of running this project
      1. self.account_pool = getAccountPoolFromDisk() -> account_pool: array
      2. self.account_pool = updateAccountPool(account_pool) -> account_pool: array
      3. updateAccountPool -> (updateAccountIp (ip), checkAccount(if can get the goods data)) remove account from account_pool if account is unavailable
      4. upateAccountIp(ip) -> ip: str (if ip is alive, return it, else return a new ip)
    2. getAccounts(rest_num) -> (get another rest_num = num - len(account_pool) accounts)
    3. saveAccountPool -> (save account_pool into disk)

3. main:
   1. num thread, each sleep num sec every time.
   2. catch exception and do -> 
      1. pass
      2. update ip
      3. removeAccount
   3. saveAccountPool


4. Others:
   1. check ip address online: https://icanhazip.com/   https://httpbin.org/ip
   2. session.post or session.get 和 post或get的区别：session可以保存cookie、headers等信息，保存连接信息；而post或get用完就销毁了，每次调用都要指定headers、cookies等通用信息。
tip: some threads will get the same lowest item, so if i need buy this item, should save this item id into a list first. avoiding the buyer account repost more than once.



5. use a main account buy items, and others just browse the lowest price items, and store the item id into like list, the main account iterate the list and buy the item one by one. -- update on 2024/09/17