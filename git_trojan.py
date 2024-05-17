# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/17 21:08
"""
import base64
import github3
import importlib
import json
import random
import sys
import threading
import time

from datetime import datetime


def github_connect():
    with open('mytoken.txt') as fp:
        token = fp.read()
    user = 'tiarno'
    sess = github3.login(token=token)
    return sess.repository(user, '')


