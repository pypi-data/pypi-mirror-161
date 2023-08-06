import requests

def login(id,password,pin):
    data = {"fy_id": id,"password": password,"app_id": "2","imei": "","recaptcha_token": ""}
    r = requests.post('https://api.fyers.in/vagator/v1/login', json=data)
    request_key = r.json()['request_key']
    data2 = {"request_key": request_key, "identity_type": "pin", "identifier": pin, "recaptcha_token": ""}
    r2 = requests.post('https://api.fyers.in/vagator/v1/verify_pin', json=data2)
    refresh_token = r2.json()['data']['refresh_token']
    access_token = r2.json()['data']['access_token']
    headers = {'authorization': access_token, }
    return headers

def fund(access_token):
    r = requests.get('https://api.fyers.in/fydev/v1/funds', headers=access_token)
    margin_used = r.json()['fund_limit'][6]['equityAmount']
    available_margin = r.json()['fund_limit'][9]['equityAmount']
    ledger_balance = r.json()['fund_limit'][0]['equityAmount']
    return margin_used,available_margin,ledger_balance

def order_history(access_token):
    r = requests.get('https://api.fyers.in/fydev/v1/orders', headers=access_token)
    orders = r.json()['orderBook']
    return orders

def trade_history(access_token):
    r = requests.get('https://api.fyers.in/fydev/v1/tradebook', headers=access_token)
    trades = r.json()['tradeBook']
    return trades
def holding(access_token):
    r = requests.get('https://api.fyers.in/fydev/v1/holdings', headers=access_token)
    holdings = r.json()['tradeBook']
    return holdings
def place_order(access_token,productType,side,exchange,symbol,qty,type,filledQty,limitPrice,stopPrice):
    json_data = {
        'noConfirm': True,
        'productType': productType,
        'side': 1 if side =="BUY" else -1,
        'symbol': f'{exchange}:{symbol}',
        'qty': int(qty),
        'disclosedQty': 0,
        'type': int(type),
        'LTP': 0,
        'validity': 'DAY',
        'filledQty': int(filledQty),
        'limitPrice': float(limitPrice),
        'stopPrice': float(stopPrice),
        'offlineOrder': False,
    }
    r = requests.post('https://api.fyers.in/fydev/v1/orders',  headers=access_token, json=json_data)
    data = r.json()
    return data
