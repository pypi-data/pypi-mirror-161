import requests, os, time
from .userCheck import userCheck

class ASGIHandler:
    def asgi_get_handler(scope):
        query_string = scope.get('headers')
        host = ''
        operator = ''
        token = ''
        can_auth = 0
        print(query_string)
        for i in query_string:
            if i[0].decode() == 'origin':
                host = i[1].decode().split('//')[1]
                if host.startswith('192'):
                    if host.startswith('127'):
                        if host.startswith('localhost'):
                            can_auth = 1
                        else:
                            can_auth = 0
                    else:
                        can_auth = 0
                else:
                    can_auth = 0
            elif i[0].decode() == 'operator':
                operator = i[1].decode()
                continue
            elif i[0].decode() == 'token':
                token = i[1].decode()
                continue
            else:
                continue
        if can_auth == 1 and operator != '' and token != '':
            user_check_data = host + ',' + operator + ',' + token
            print(user_check_data)
            license_dir = 'Authorization'
            if license_dir.is_dir() is False:
                os.mkdir('Authorization')
            filePath = 'Authorization/License.txt'
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
                    userCheck.get_auth_check(host, operator, token)
                    with open(filePath, "a", encoding='utf-8') as f:
                        f.write(user_check_data + "\n")
                    f.close()
            else:
                userCheck.get_auth_check(host, operator, token)
                with open(filePath, "w", encoding='utf-8') as f:
                    f.write(user_check_data + "\n")
                f.close()