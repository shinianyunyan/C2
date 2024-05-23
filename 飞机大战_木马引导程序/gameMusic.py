# -*- coding:utf-8 -*-
"""
作者：shinian
日期：2022/12/19 10:58
"""
import os

import pygame


class MusicPlayer(object):
    """音乐播放器"""
    resPath = "./res/sound/"

    def __init__(self, music_file):
        """初始化音乐播放器"""
        # 加载背景音乐
        pygame.mixer.music.load(self.resPath + music_file)
        pygame.mixer.music.set_volume(0.2)

        # 初始化音效的字典
        self.soundDict = {}
        files = os.listdir(self.resPath)
        for file in files:
            if file == music_file:  # 背景音乐不加载
                continue

            sound = pygame.mixer.Sound(self.resPath + file)
            self.soundDict[file] = sound

    @staticmethod
    def playMusic():
        """播放背景音乐"""
        pygame.mixer.music.play(-1)

    @staticmethod
    def pauseMusic(is_pause):
        """根据暂停状态判断是否要播放音乐"""
        if is_pause:  # 暂停
            pygame.mixer.music.pause()
        else:  # 播放
            pygame.mixer.music.unpause()

    def playSound(self, wav_name):
        """根据文件名播放音效"""
        self.soundDict[wav_name].play()
        self.soundDict[wav_name].set_volume(0.3)
