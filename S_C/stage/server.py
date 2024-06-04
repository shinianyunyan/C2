# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/24 22:01
"""
# stage/server.py
import signal  # 导入处理信号的模块，用于处理中断信号（Ctrl+C）
import sys  # 导入系统模块，提供对Python解释器的访问
import threading  # 导入线程模块，用于创建和管理线程
import time  # 导入时间模块，提供时间相关的功能

from flask import Flask  # 导入Flask框架，用于创建Web应用

from .handlers import *

# 创建Flask应用实例
app = Flask(__name__)
app.secret_key = 's3cr3t_k3y_h3r3_@128!#asd'  # 设置用于加密会话数据的密钥
login_manager.init_app(app)  # 初始化Flask-Login插件
IP = "192.168.117.190"  # 服务端ip

# 添加URL规则，将URL路径映射到对应的处理函数
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])  # 登录页面的路由，支持GET和POST方法
app.add_url_rule('/', 'login', login, methods=['GET', 'POST'])  # 根路径重定向到登录页面，支持GET和POST方法
app.add_url_rule('/index', 'index', login_required(index))  # 主页的路由，需登录后访问
app.add_url_rule('/pcinfo', 'get_pcinfo', get_pcinfo, methods=['GET'])  # /pcinfo 路由映射到get_pcinfo函数，仅支持GET方法
app.add_url_rule('/save_info/', 'save_info', save_info, methods=['POST'])  # /save_info/ 路由映射到save_info函数，仅支持POST方法
app.add_url_rule('/print_info', 'print_info', print_info)  # /print_info 路由映射到print_info函数
app.add_url_rule('/activate/', 'activate', activate, methods=['POST'])  # /activate/ 路由映射到activate函数，仅支持POST方法
app.add_url_rule('/result/', 'result', result, methods=['GET', 'POST'])  # /result 路由映射到result函数，支持GET和POST方法
app.add_url_rule('/print_result/<ip>', 'print_result', print_result)  # /print_result/<ip> 路由映射到print_result函数
app.add_url_rule('/screenshotter/', 'screenshotter', screenshotter, methods=['GET', 'POST'])  # 获取截图的路由，支持GET和POST方法
app.add_url_rule('/logout', 'logout', logout)  # 退出登录的路由


def run_server():
    """
    启动Flask服务器，监听指定IP和端口。
    """
    app.run(f'{IP}', 8080, False)  # 启动Flask应用，监听192.168.223.190:8080


def signal_handler(sig, frame):
    """
    信号处理函数，用于处理Ctrl+C中断信号。
    """
    print('You pressed Ctrl+C!')  # 打印中断信号消息
    sys.exit(0)  # 退出程序


def main():
    """
    主函数，设置信号处理并启动服务器线程。
    """
    signal.signal(signal.SIGINT, signal_handler)  # 绑定SIGINT信号到signal_handler函数

    # 创建并启动服务器线程
    server_thread = threading.Thread(target=run_server)  # 创建服务器线程，目标函数为run_server
    server_thread.start()  # 启动服务器线程

    try:
        # 主线程循环等待
        while True:
            time.sleep(1)  # 主线程每秒休眠一次，保持活跃
    except KeyboardInterrupt:
        # 捕获键盘中断，打印消息并退出
        print('Main thread interrupted. Exiting...')  # 打印中断消息
        sys.exit(0)  # 退出程序


if __name__ == '__main__':
    app.run(debug=True)  # 如果脚本直接运行，则启动Flask应用，启用调试模式
