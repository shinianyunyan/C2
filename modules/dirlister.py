# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/17 20:42
"""
import os


def run(**args):
    print("[*] In dirlister module")
    files = os.listdir(".")  # 列出当前目录下的所有文件
    return str(files)  # 返回所有文件名

