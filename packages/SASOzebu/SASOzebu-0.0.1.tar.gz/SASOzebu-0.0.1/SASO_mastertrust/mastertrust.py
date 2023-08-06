import requests

class mastertrust:

    def login(self,login_id,password,YOB):
        json_data = {'login_id': login_id.upper(), 'password': password, 'device': 'WEB', }
        response = requests.post('https://masterswift-beta.mastertrust.co.in/api/v1/user/login', json=json_data)
        twofa_token = response.json()['data']['twofa_token']
        json_data = {'login_id': login_id.upper(), 'twofa': [{'question_id': 1, 'answer': YOB, }, ],'twofa_token': twofa_token, }
        r = requests.post('https://masterswift-beta.mastertrust.co.in/api/v1/user/twofa', json=json_data)
        auth_token = r.json()['data']['auth_token']
        token = {'X-Authorization-Token': auth_token}
        return token

    def fund(self,token):
        params = {'client_id': '0','type': 'all',}
        r = requests.get('https://masterswift-beta.mastertrust.co.in/api/v1/funds/view', params=params,  headers=token)
        return r.json()

    def orderhistory(self,token):
        params = {'type': 'completed','client_id': '1',}
        r = requests.get('https://masterswift-beta.mastertrust.co.in/api/v1/orders', params=params,  headers=token)
        return r.json()

    def pendingorderhistory(self,token):
        params = {'type': 'pending','client_id': '1',}
        r = requests.get('https://masterswift-beta.mastertrust.co.in/api/v1/orders', params=params,  headers=token)
        return r.json()

    def tradehistory(self,token):
        r = requests.get('https://masterswift-beta.mastertrust.co.in/api/v1/trades',  headers=token)
        return r.json()

    def place_order(self,token,exchange,instrument_token,order_type,price,quantity,product,order_side,trigger_price,stop_loss_value,square_off_value,trailing_stop_loss):
        json_data = {
            'exchange': exchange,
            'instrument_token':int(instrument_token),
            'client_id': '',
            'order_type': order_type,
            'price': float(price),
            'quantity': int(quantity),
            'disclosed_quantity': 0,
            'validity': 'DAY',
            'product': product,
            'order_side': order_side,
            'device': 'WEB',
            'user_order_id': 0,
            'trigger_price': float(trigger_price),
            'stop_loss_value': float(stop_loss_value),
            'square_off_value': float(square_off_value),
            'trailing_stop_loss': float(trailing_stop_loss),
            'is_trailing': False,
        }
        r = requests.post('https://masterswift-beta.mastertrust.co.in/api/v1/orders',  headers=token, json=json_data)
        return r.json()

