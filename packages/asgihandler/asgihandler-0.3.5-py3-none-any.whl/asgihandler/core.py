import requests, os, time
from .userCheck import userCheck

class ASGIHandler:
    def asgi_get_handler(scope):
        query_string = scope.get('headers')
        operator = ''
        token = ''
        for i in query_string:
            if i[0].decode() == 'operator':
                operator = i[1].decode()
                continue
            elif i[0].decode() == 'token':
                token = i[1].decode()
                continue
            else:
                continue
        if operator != '' and token != '':
            user_check_data = operator + ',' + token
            filePath = 'License.txt'
            auth_license = False
            if os.path.exists(filePath) is True:
                with open(filePath, "r", encoding='utf-8') as f:
                    line = f.readlines()
                    for line_list in line:
                        line_new = line_list.replace('\n', '')
                        if line_new != user_check_data:
                            auth_license = True
                        else:
                            auth_license = False
                f.close()
                if auth_license is True:
                    userCheck.get_auth_check(scope)
                    with open(filePath, "a", encoding='utf-8') as f:
                        f.write(user_check_data + "\n")
                    f.close()
            else:
                userCheck.get_auth_check(scope)
                with open(filePath, "w", encoding='utf-8') as f:
                    f.write(user_check_data + "\n")
                f.close()