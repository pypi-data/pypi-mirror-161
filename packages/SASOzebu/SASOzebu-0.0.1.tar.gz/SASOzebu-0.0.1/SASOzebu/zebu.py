import requests

class zebu:
    def login(self,userId,mpin):
        json_data = {'mpin': mpin,'userId': userId,}
        r = requests.post('https://api.zebull.in/rest/V2MobullService/sso/verifyMpin', json=json_data)
        userSessionID = r.json()['userSessionID']
        return userSessionID
    
    def orderhistory(self,userId,userSessionID):
        headers = {'Authorization': f'Bearer {userId} {userSessionID}'}
        json_data = {'userSessionID': userSessionID,'userId': userId,
                     'userSettingDto': {'exch': [ 'NSE',],'s_prdt_ali': 'NRML:NRML||MIS:MIS||CNC:CNC||CO:CO||BO:BO',},}
        r = requests.post('https://api.zebull.in/rest/V2MobullService/placeOrder/fetchOrderBook', headers=headers, json=json_data)
        return r.json()
    
    def tradehistory(self,userId,userSessionID):
        headers = {'Authorization': f'Bearer {userId} {userSessionID}'}
        json_data = {'userSessionID': userSessionID,'userId': userId,
                    'userSettingDto': {'exch': [ 'NSE',],'s_prdt_ali': 'NRML:NRML||MIS:MIS||CNC:CNC||CO:CO||BO:BO',},}
        r= requests.post('https://api.zebull.in/rest/V2MobullService/placeOrder/fetchTradeBook', headers=headers, json=json_data)
        return r.json()
    
    def holding(self,userId,userSessionID):
        headers = {'Authorization': f'Bearer {userId} {userSessionID}'}
        json_data = {'userSessionID': userSessionID,'userId': userId,
            'userSettingDto': {'s_prdt_ali': 'NRML:NRML||MIS:MIS||CNC:CNC||CO:CO||BO:BO',
            'broker_name': 'ZEBU','account_id': userId,},}
        r= requests.post('https://api.zebull.in/rest/V2MobullService/positionAndHoldings/holdings', headers=headers, json=json_data)
        return r.json()
    
    def liveprice(self,userId,userSessionID,exch,symboltoken):
        headers = {'Authorization': f'Bearer {userId} {userSessionID}'}
        json_data = {'exch': exch,'symbol': symboltoken,'userId': userId,'userSessionID': userSessionID,}
        r = requests.post('https://api.zebull.in/rest/V2MobullService/ScripDetails/getPriceRange', headers=headers, json=json_data)
        dt = r.json()
        marketdata = {'Symbol':dt['Symbol'],'Open':dt['openrate'],'High':dt['highrate'],'Low':dt['lowrate'],'Close':dt['previouscloserate'],'LTP':dt['Ltp']}
        return marketdata
    
    def place_order(self,userId,userSessionID,complexty,discqty,exch,pCode,prctyp,price,qty,stopLoss,symbol_id,target,trading_symbol,trailing_stop_loss,transtype,trigPrice):
        headers = {'Authorization': f'Bearer {userId} {userSessionID}'}
        json_data = [
            {
                'complexty': complexty,
                'discqty': int(discqty),
                'exch': exch,
                'master_id': 0,
                'pCode': pCode,
                'prctyp': prctyp,
                'price': int(price),
                'qty': int(qty),
                'ret': 'DAY',
                'stopLoss': stopLoss,
                'symbol_id': int(symbol_id),
                'target': float(target),
                'trading_symbol': trading_symbol,
                'trailing_stop_loss': int(trailing_stop_loss),
                'transtype': transtype,
                'trigPrice': int(trigPrice),
                'userId': userId,
                'userSessionID': userSessionID,
                'userSettingDto': {'s_prdt_ali': 'NRML:NRML||MIS:MIS||CNC:CNC||CO:CO||BO:BO','account_id': userId,},},]
    
        r = requests.post('https://api.zebull.in/rest/V2MobullService/placeOrder/executePlaceOrder', headers=headers, json=json_data)
        return r.json()









