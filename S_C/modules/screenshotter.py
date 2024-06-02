# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/19 21:21
"""
import os  # 导入操作系统模块

import win32gui  # 导入 Windows GUI 模块
from PyQt5.QtWidgets import QApplication  # 导入 PyQt5 应用程序模块


def screenshot():
    """
    截取屏幕截图并保存为图片文件
    """
    hwnd = win32gui.FindWindow(None, 'c:\Windows\system32\cmd.exe')  # 获取命令提示符窗口句柄
    app = QApplication([])  # 创建一个 PyQt5 应用程序对象
    screen = QApplication.primaryScreen()  # 获取主屏幕对象
    img = screen.grabWindow(hwnd).toImage()  # 截取窗口截图并转换为图像对象
    img.save("screenshot.jpg")  # 将图像保存为图片文件


def run():
    """
    执行截图并返回图像字节数据
    """
    print("[*] In screenshotter module")  # 打印调试信息
    screenshot()  # 截取屏幕截图
    with open('screenshot.jpg', 'rb') as f:  # 以二进制模式读取图像文件
        img_data = f.read()  # 读取图像字节数据
    os.remove('screenshot.jpg')  # 删除临时生成的截图文件
    print('The screenshotter module is done.')
    return img_data  # 返回图像字节数据


if __name__ == '__main__':
    screenshot()  # 在运行时执行截图操作
