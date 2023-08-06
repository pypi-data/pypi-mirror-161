import requests
import base64

class upstox:
    def login(self,userId,password,YOB):
        message = str(password)
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        pwd = base64_bytes.decode('ascii')
        params = {'requestId': '0',}
        json_data = {'data': {'loginMethod': 'OMS','userId': userId,'password': pwd,},}
        r = requests.post('https://service.upstox.com/login/open/v2/auth/1fa', params=params,  json=json_data)
        tokenFor2FA = r.json()['data']['tokenFor2FA']
        headers = {'x-device-details': 'platform=WEB|osName=Windows/10|osVersion=Chrome/103.0.0.0|appVersion=1.3.3|manufacturer=unknown|modelName=Chrome',}
        params = {'requestId': '0','client_id': 'DCS-TYasnEfnL5ydgqK3I9AL478Q','response_type': 'code','redirect_uri': 'https://developer.upstox.com/auth',}
        data = {'data': {'twoFAMethod': 'YOB', 'userId': userId, 'inputText': YOB,'tokenFor2FA': tokenFor2FA,'enableBiometrics': True,},}
        r = requests.post('https://service.upstox.com/login/open/v2/auth/2fa', params=params, headers=headers, json=data)
        access_token = r.cookies.get_dict()['access_token']
        refresh_token = r.cookies.get_dict()['refresh_token']
        cookies = cookies = { 'access_token': access_token,'refresh_token': refresh_token,}
        return cookies

    def fund(self,cookies):
        r = requests.get('https://service.upstox.com/payout/v0/limits/sec',  cookies=cookies)
        return r.json()

    def order_history(self,cookies):
        r = requests.get('https://service.upstox.com/portfolio/v0/orderbook', cookies=cookies,)
        return list(dict(r.json()['data']).values())

    def place_order(self,cookies,exchange,token,series,order_type,product,transaction_type,price,trigger_price,quantity):
        json_data = {
            'data': {
                'exchange': f'{exchange}_{series}',
                'token': token,
                'symbol': '',
                'series': series,
                'is_amo': False,
                'order_complexity':'SIMPLE',
                'order_type': order_type,
                'product': product,
                'duration': 'DAY',
                'transaction_type': transaction_type,
                'price': price,
                'trigger_price': trigger_price,
                'disclosed_quantity': '0',
                'quantity': quantity,
            },
        }
        r = requests.post('https://service.upstox.com/interactive/v1/order', cookies=cookies, json=json_data)
        return r.json()

