import json
import yaml
import random
import consul
import requests
import logging
import os


class ConsulClient:
    def __init__(self, host=None, port=None, token=None):
        self.host = host
        self.port = port
        self.token = token
        self.consul = consul.Consul(host=host, port=port)
        self.registered = False

    def register(self, name, service_id, address, port, tags, http_check_url):
        # 注册新的微服务节点之前，先去注册Consul中可能残存的本节点信息（例如微服务停止后在Consul中尚未清除之前就重新启动）
        url = 'http://{}:{}/v1/health/service/{}'.format(self.host,self.port, name)
        res = requests.get(url)
        if res.status_code == 200:
            instances = json.loads(res.text)
            for instance in instances:
                if instance['Service']['Address'] == address and instance['Service']['Port'] == port:
                    self.consul.agent.service.deregister(instance['Service']['ID'])

        # 注册微服务
        try:
            self.consul.agent.service.register(
                name,
                service_id=service_id,
                address=address,
                port=port,
                tags=tags,
                check=consul.Check().http(http_check_url, '10s', '20s', '20s')
            )
            self.registered = True
            logging.critical('Successful registered to Consul: {}:{}'.format(address, port))
        except:
            self.registered = False

    def get_services(self):
        return self.consul.agent.services()

    def resolve_service(self, name):  # 根据服务名解析其“IP地址:端口号”，负载均衡随机取其中之一
        # 如果程序运行在K8S中，直接通过kube-dns解析服务名，服务端口号默认为80
        if os.environ.get('APP_PROFILE', 'dev').lower() == 'k8s':
            return name

        # 非k8s环境，从Consul解析地址
        url = 'http://{}:{}/v1/health/service/{}'.format(self.host,self.port, name)
        res = requests.get(url)
        if res.status_code != 200:
            return None

        instances = json.loads(res.text)
        results = []
        for instance in instances:
            if instance['Checks'][0]['Status'] == 'passing':
                results.append(instance['Service']['Address'] + ':' + str(instance['Service']['Port']))

        if len(results) > 0:
            return results[random.randint(0, len(results) - 1)]  # 随机获取一个可用的服务实例

        return None

    def get_kv(self):
        try:
            kv_yaml = self.consul.kv.get('config/application/data')[1].get('Value')
            return yaml.load(kv_yaml, Loader=yaml.SafeLoader)
        except:
            return None


if __name__ == "__main__":
    consul_client = ConsulClient('127.0.0.1', 8500)
    consul_client.register('demo',  'demo-test', '127.0.0.1', 8888, ['profile-dev'], 'http://127.0.0.1:8888/management/health')
    if consul_client.registered:
        print('Registered in Consul!')
        print(consul_client.resolve_service('uaa'))
        print(consul_client.resolve_service('demo'))
        print(consul_client.get_kv())
    else:
        print('Not registered in Consul!!!')

