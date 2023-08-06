import requests

class userCheck:
    def get_auth_check(host, operator, token):
        context = {
            "host": host,
            "operator": operator,
            "token": token
        }
        try:
            requests.post('http://192.168.1.3:8007/asgihandler/', json=context, timeout=3).json()
        except:
            pass