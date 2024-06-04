# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/6/6 22:39
"""
import platform
import winreg


def delete_startup_task():
    """删除启动任务"""
    if platform.system() == 'Windows':
        # 获取当前用户的注册表根键
        key = winreg.HKEY_CURRENT_USER
        # 定义注册表子键路径
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            # 打开注册表子键，准备删除值
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                # 删除指定名称的注册表项
                winreg.DeleteValue(reg_key, "client")
            print("删除自动任务成功")
        except FileNotFoundError:
            print("自动任务不存在")


# 调用函数以删除启动任务
delete_startup_task()
