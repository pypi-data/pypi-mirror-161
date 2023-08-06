import requests
def login(clientid,Pass,YOB):
    json_data = {
        'login_id': clientid,
        'password': Pass,
        'device': 'WEB',
    }
    response = requests.post('https://ant.aliceblueonline.com/api/v1/user/login', json=json_data)
    twofa_token = response.json()['data']['twofa']['twofa_token']
    json_data = {
        'login_id': clientid,
        'twofa': [{'question_id': '1', 'answer': YOB, }, ],
        'twofa_token': twofa_token,
        'type': 'GENERAL_QUESTIONS',
    }
    response = requests.post('https://ant.aliceblueonline.com/api/v1/user/twofa', json=json_data)
    auth_token = response.json()['data']['auth_token']
    headers = {'x-authorization-token': auth_token}
    return headers

def fund(auth_token):
    params = {'client_id': '0', 'type':'all'}
    response = requests.get('https://ant.aliceblueonline.com/api/v1/funds/view', params=params,  headers=auth_token)
    fnd = response.json()
    return fnd

def order_history(auth_token):
    params = {'type': 'completed','client_id': '0',}
    response = requests.get('https://ant.aliceblueonline.com/api/v1/orders', params=params, headers=auth_token)
    orders = response.json()
    return orders

def trade_history(auth_token):
    params = {'type': 'Trades','client_id': '0',}
    response = requests.get('https://ant.aliceblueonline.com/api/v1/trades', params=params, headers=auth_token)
    trades = response.json()
    return trades

def pending_order_history(auth_token):
    params = {'type': 'pending','client_id': '0',}
    response = requests.get('https://ant.aliceblueonline.com/api/v1/pending', params=params, headers=auth_token)
    pendings = response.json()
    return pendings

def holdings(auth_token):
    params = {'product_code': '','client_id': '0',}
    r = requests.get('https://ant.aliceblueonline.com/api/v1/holdings', params=params,headers=auth_token)
    holdings = r.json()['data']['holdings']
    return holdings

def place_order(auth_token,exchange,instrument_token,order_type,price,quantity,product,order_side,trigger_price,stop_loss_value,square_off_value,trailing_stop_loss):
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
    r = requests.post('https://ant.aliceblueonline.com/api/v1/orders',headers=auth_token,json=json_data)
    return r.json()

def cancel_pending_order(auth_token,client_order_id):
    params = {'client_id': '0',}
    r = requests.delete(f'https://ant.aliceblueonline.com/api/v1/orders/{client_order_id}',params=params, headers=auth_token)
    return r.json()
