import sys
import json
import yaml
import getpass
import requests
from urllib.parse import quote
from urllib3 import encode_multipart_formdata


def get_tokens(url_server):
    url_login = '{}/api/data'.format(url_server)

    print('即将向CubeAI平台({})推送模型并生成微服务...'.format(url_server))
    print('请输入你在CubeAI平台({})注册的用户名和口令：\n'.format(url_server))
    username = input('username: ')
    password = getpass.getpass('password: ')

    body = {
        'action': 'login_cmd',
        'args': {
            'username': username,
            'password': password,
        }
    }

    try:
        res = requests.post(url_login, json=body)
    except:
        return 'error:网站 {} 无法访问！'.format(url_server)

    res = json.loads(res.text, encoding='utf-8')

    if res['status'] == 'ok':
        tokens = res['value']
        return 'refresh_token={}; access_token={}'.format(tokens['refresh_token'], tokens['access_token'])
    else:
        return 'error:用户名或密码错误！'


def get_file_name():
    try:
        with open('./application.yml', 'rb') as f:
            yml = yaml.load(f, Loader=yaml.SafeLoader)
    except:
        print('错误： 模型配置文件application.yml不存在！')
        return None

    try:
        name = yml['serviceboot']['cname']
    except:
        print('错误： 未指定模型名称！')
        print('请在application.yml文件中使用属性 serviceboot.cname 指定...')
        return None

    return '{}.zip'.format(name)


def onboarding():
    if len(sys.argv) > 2:
        url_server = sys.argv[2]
    else:
        url_server = 'https://cubeai.org'

    file_name = get_file_name()
    if file_name is None:
        return

    tokens = get_tokens(url_server)
    if tokens.startswith('error:'):
        print(tokens[6:])
        return

    data = {
        'onboard_model': (file_name, open('out/{}'.format(file_name), 'rb').read())
    }
    encode_data = encode_multipart_formdata(data)

    headers = {
        'Content-Type': encode_data[1],
        'Cookie': tokens,
    }

    url_onboarding = '{}/umu/api/file/onboard_model'.format(url_server)
    res = requests.post(url_onboarding, headers=headers, data=encode_data[0])
    res = json.loads(res.text, encoding='utf-8')
    if res['status'] == 'ok':
        task_uuid = res['value']
        url_task = '{}/ms/pmodelhub/#/task-onboarding/{}/{}'.format(url_server, task_uuid, quote(file_name, 'utf-8'))
        print('文件上传成功！正在生成微服务...')
        print('请打开CubeAI平台任务详情页面查看模型导入进度： {} \n'.format(url_task))
    else:
        print('文件上传失败： {}'.format(res['value']))


if __name__ == '__main__':
    onboarding()
