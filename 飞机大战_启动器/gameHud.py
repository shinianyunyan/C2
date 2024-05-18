# -*- coding:utf-8 -*-
"""
作者：shinian
日期：2022/12/19 10:58
"""
import pygame

from gameItems import *

"""游戏控制面板/提示信息模块"""


class HUDPanel(object):
    """所有面板精灵的控制类"""
    margin = 10  # 精灵间距
    white = (255, 255, 255)  # 白色底纹
    gray = (64, 64, 64)  # 灰色

    rewardScore = 100000  # 奖励得分
    level2Score = 10000  # 2级
    level3Score = 50000  # 3级

    recordFileName = "record.txt"

    def __init__(self, display_group):
        # 基本数据
        self.bombCount = HERO_BOMB_COUNT
        self.score = 0  # 游戏得分
        self.livesCount = 3  # 生命计数
        self.level = 1  # 英雄级别
        self.bestScore = self.loadBestScore()  # 最好成绩

        # 图像精灵
        # 状态按钮
        self.statusSprite = StatusButton(("pause_nor.png", "resume_nor.png"), display_group)
        # 将暂停/开始按钮放置在左上角
        self.statusSprite.rect.topleft = (self.margin, self.margin)

        # 得分标签
        self.scoreLabel = Label(f"{int(self.score)}", 32, self.gray, display_group)
        # 将得分标签放置在开始/暂停按钮的左侧加一个间距，并与其保持水平对齐
        self.scoreLabel.rect.midleft = (self.statusSprite.rect.right + self.margin, self.statusSprite.rect.centery)

        # 炸弹精灵
        self.bombSprite = GameSprite("bomb.png", 0, display_group)
        self.bombSprite.rect.left = self.margin  # 左边距
        self.bombSprite.rect.bottom = SCREEN_RECT.bottom - self.margin  # 下边距

        # 炸弹计数标签
        self.bombLabel = Label("X 3", 32, self.gray, display_group)
        # 将标签放置在炸弹精灵右侧加一个间距，并与其保持水平对齐
        self.bombLabel.rect.midleft = (self.bombSprite.rect.right + self.margin, self.bombSprite.rect.centery)

        # 生命计数标签（数值）
        self.livesLabel = Label(f"X {int(self.livesCount)}", 32, self.gray, display_group)
        # 将标签放置在窗口的右侧负一个间距，并与炸弹精灵保持水平对齐
        self.livesLabel.rect.midright = (SCREEN_RECT.right - self.margin, self.bombSprite.rect.centery)

        # 生命精灵
        self.livesSprite = GameSprite("life.png", 0, display_group)
        # 生命精灵的右侧在生命值左侧一个间距
        self.livesSprite.rect.right = self.livesLabel.rect.left - self.margin  # 右边距
        # 生命精灵下部在窗口下部的负一个间距
        self.livesSprite.rect.bottom = SCREEN_RECT.bottom - self.margin  # 下边距

        # 最好成绩标签
        self.bestLabel = Label(f"Best: {self.loadBestScore()}", 36, self.white)
        # 将标签放置在窗口中心
        self.bestLabel.rect.center = SCREEN_RECT.center

        # 状态标签
        self.statusLabel = Label("Game Paused!", 48, self.white)
        # 让标签与最好成绩保持竖直对齐，在最好成绩的下方两个间距
        self.statusLabel.rect.midbottom = (self.bestLabel.rect.centerx, self.bestLabel.rect.y - 2 * self.margin)

        # 提示标签
        self.tipLabel = Label("Press spacebar to continue.", 22, self.white)
        # 使标签与最好成绩保持竖直对齐，并距最好成绩底部八个间距
        self.tipLabel.rect.midtop = (self.bestLabel.rect.centerx, self.bestLabel.rect.bottom + 8 * self.margin)

        # 从文件中加载最好成绩
        self.loadBestScore()

    def showBomb(self, bomb_count):
        """修改炸弹数量为 X count"""
        self.bombLabel.setText(f"X {bomb_count}")
        # 将标签放置在炸弹精灵的右侧加一个间距
        self.bombLabel.rect.midleft = (self.bombSprite.rect.right + self.margin, self.bombSprite.rect.centery)

    def showLives(self):
        """显示最新的生命计数为 X livesCount"""
        self.livesLabel.setText(f"X {int(self.livesCount)}")

        # 修正生命计数精灵的位置
        # 将标签放置在窗口右侧负一个间距，并与炸弹精灵的中心保持水平对齐
        self.livesLabel.rect.midright = (SCREEN_RECT.right - self.margin, self.bombSprite.rect.centery)

        # 修正生命计数精灵的位置
        # 生命精灵的右侧在生命值标签的左侧负一个间距
        self.livesSprite.rect.right = self.livesLabel.rect.left - self.margin
        # 生命精灵的下部在窗口下部的负一个间距
        self.livesSprite.rect.bottom = SCREEN_RECT.bottom - self.margin

    def increaseScore(self, enemy_score):
        """增加得分，同时要增加生命，关卡升级，最好成绩更新"""
        # 计算最高得分
        score = self.score + enemy_score  # 最终得分为上次计分加敌机得分

        # 判断是否增加生命
        # 当当前分数对奖励分数取整的值不等于上次得分对奖励分数取整的值时为True
        if score // self.rewardScore != self.score // self.rewardScore:
            self.livesCount += 1
            self.showLives()

        # 不论是否增加生命值，更新分值
        self.score = score

        # 更新最好成绩
        self.bestScore = score if score > self.bestScore else self.bestScore

        # 计算最新关卡等级
        if score < self.level2Score:
            level = 1
        elif score < self.level3Score:
            level = 2
        else:
            level = 3

        isUpgrade = level != self.level
        self.level = level

        # 更新得分的精灵显示内容
        self.scoreLabel.setText(str(score))
        # 将得分标签放置在开始/暂停按钮的左侧加一个间距，并与其保持水平对齐
        self.scoreLabel.rect.midleft = (self.statusSprite.rect.right + self.margin, self.statusSprite.rect.centery)

        # 返回是否升级给游戏主逻辑
        return isUpgrade

    def saveBestScore(self, score):
        """保存最好成绩"""
        file = open(self.recordFileName, "w")
        file.write(str(score))
        file.close()

    def loadBestScore(self):
        """从文件中获取最高得分"""
        try:
            file = open(self.recordFileName, "r")
            content = file.read()
            file.close()

            # self.bestScore = int(content)
            return int(content)
        except (FileNotFoundError, ValueError):
            print("读取最高得分文件，发生异常！")

    def panelPaused(self, is_game_over, display_group):
        """暂停游戏显示提示信息，is_game_over 为True 说明游戏结束，，为False 说明游戏暂停"""
        # 判断是否已经显示提示信息
        if display_group.has(self.bestLabel, self.statusLabel, self.tipLabel):
            return

        # 根据游戏状态生成提示信息
        status = "Game Over!" if is_game_over else "Game Pause!"
        tip = "Press spacebar to "
        tip += "Play again." if is_game_over else "Continue."

        # 修改标签精灵的文本内容
        self.bestLabel.setText("Best {}".format(int(self.bestScore)))
        self.statusLabel.setText(status)
        self.tipLabel.setText(tip)

        # 修正标签精灵的位置
        self.bestLabel.rect.center = SCREEN_RECT.center
        self.statusLabel.rect.midbottom = (self.bestLabel.rect.centerx, self.bestLabel.rect.y - 2 * self.margin)
        self.tipLabel.rect.midtop = (self.bestLabel.rect.centerx, self.bestLabel.rect.bottom + 8 * self.margin)

        # 将标签精灵添加到精灵组
        display_group.add(self.bestLabel, self.statusLabel, self.tipLabel)

        # 修改状态按钮
        self.statusSprite.switchStatus(True)

    def panelResume(self, display_group):
        """隐藏提示信息"""
        display_group.remove(self.bestLabel, self.statusLabel, self.tipLabel)
        # 恢复状态按钮
        self.statusSprite.switchStatus(False)

    def resetPanel(self):
        """重置面板数据"""
        # 重置数据
        self.score = 0
        self.livesCount = 3

        # 重置精灵数据
        self.increaseScore(0)
        self.showBomb(self.bombCount)
        self.showLives()
