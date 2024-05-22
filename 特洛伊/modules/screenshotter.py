# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/19 21:21
"""
import sys

import win32gui
from PyQt5.QtWidgets import QApplication


def screenshot():
    hwnd = win32gui.FindWindow(None, 'c:\Windows\system32\cmd.exe')
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(hwnd).toImage()
    img.save("screenshot.jpg")


def run():
    print("[*] In screenshotter module")
    screenshot()
    with open('screenshot.jpg', 'rb') as f:  # 修改为以二进制模式读取
        img = f.read()
    return img


if __name__ == '__main__':
    screenshot()
