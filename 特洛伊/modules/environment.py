# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/17 21:02
"""
import os


# 收集设备上的所有环境变量
def run(**args):
    print("[*] In environment module.")
    return os.environ
