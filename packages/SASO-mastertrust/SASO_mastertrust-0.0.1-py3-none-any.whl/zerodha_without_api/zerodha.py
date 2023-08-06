import requests

def login(user_id,password,pin):
    try:
        r = requests.get('https://kite.zerodha.com/')
        session_cookies = r.cookies
        kf_session = session_cookies.get_dict()['kf_session']
        headers = {
            'cookie': f'_ga=GA1.2.1118120826.1632217744; signup_csrftoken=UxL0mcRzSKeIuwLqyQhMm95do2aELzoZI9Zz2NLaJ5b0igV90oyG8yHukHyXOIJ6; kf_session={kf_session}', }
        data = {'user_id': user_id, 'password': password, }
        rs = requests.post('https://kite.zerodha.com/api/login', headers=headers, data=data)
        request_id = rs.json()['data']['request_id']
        data = {
            'user_id': user_id,
            'request_id': request_id,
            'twofa_value': pin,
            'skip_session': '',
        }
        r = requests.post('https://kite.zerodha.com/api/twofa', headers=headers, data=data)
        enctoken = str(r.cookies).split('enctoken=')[1].split(' for kite')[0]
        headers = {'authorization': f'enctoken {enctoken}'}
        return headers
    except:
        return 'NaN'

def profile(enctoken):
    r = requests.get('https://kite.zerodha.com/oms/user/profile/full', headers=enctoken)
    data = r.json()['data']
    return data

def fund(enctoken):
    r = requests.get('https://kite.zerodha.com/oms/user/margins',  headers=enctoken)
    data = r.json()['data']
    return data

def order_history(enctoken):
    r = requests.get('https://kite.zerodha.com/oms/orders',  headers=enctoken)
    data = r.json()['data']
    return data

def gtt_history(enctoken):
    r = requests.get('https://kite.zerodha.com/oms/gtt/triggers', headers=enctoken)
    data = r.json()['data']
    return data

def holdings(enctoken):
    r = requests.get('https://kite.zerodha.com/oms/portfolio/holdings', headers=enctoken)
    data = r.json()['data']
    return data

def place_order(enctoken,exchange,tradingsymbol,transaction_type,order_type,quantity,price,product,trigger_price,squareoff,stoploss):
    data = {
        'variety': 'regular',
        'exchange': exchange,
        'tradingsymbol': tradingsymbol,
        'transaction_type': transaction_type,
        'order_type': order_type,
        'quantity': quantity,
        'price': price,
        'product': product,
        'validity': 'DAY',
        'disclosed_quantity': 0,
        'trigger_price':trigger_price,
        'squareoff':squareoff,
        'stoploss': stoploss,
        'trailing_stoploss': 0,
        'user_id': '0'
    }
    r = requests.post('https://kite.zerodha.com/oms/orders/regular', headers=enctoken, data=data)
    data = r.json()
    return data



