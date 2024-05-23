# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/19 21:21
"""
import win32gui
from PyQt5.QtWidgets import QApplication


def screenshot():
    hwnd = win32gui.FindWindow(None, 'c:\Windows\system32\cmd.exe')
    app = QApplication([])
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(hwnd).toImage()
    img.save("screenshot.jpg")


def run():
    print("[*] In screenshotter module")
    screenshot()
    with open('screenshot.jpg', 'rb') as f:  # 以二进制模式读取图像文件
        img_data = f.read()  # 读取图像字节数据
    return img_data  # 返回图像字节数据


if __name__ == '__main__':
    screenshot()
