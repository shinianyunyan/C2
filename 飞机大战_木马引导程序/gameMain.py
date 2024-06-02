# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/23 23:47
"""
# main.py

import threading

from pygame.locals import *

from gameHud import *
from gameItems import *
from gameMusic import *


# from gameItems import handle_files, run as start_download  # 导入文件处理和下载函数

class Game(object):
    """
    核心类
    """
    def __init__(self):
        # 游戏窗口
        self.mainWindow = pygame.display.set_mode(SCREEN_RECT.size)
        pygame.display.set_caption("飞机大战")

        # 游戏状态
        self.isGameOver = False  # 游戏是否开始
        self.isGamePause = False  # 游戏是否暂停

        # 游戏精灵组
        self.allGroup = pygame.sprite.Group()  # 存放界面的所有精灵
        self.enemiesGroup = pygame.sprite.Group()  # 敌机精灵组
        self.suppliesGroup = pygame.sprite.Group()  # 道具精灵组
        self.IkunGroup = pygame.sprite.Group()  # ikun组

        # 游戏精灵
        # 创建背景精灵
        self.allGroup.add(Background(False), Background(True))  # 星空背景精灵1,2添加到组

        # 加载Ikun
        IkunSprite = Ikun([f"Ikun/kun{num}.png" for num in range(0, 54)], self.allGroup, self.IkunGroup)
        IkunSprite.rect.center = SCREEN_RECT.center

        # 创建英雄飞机精灵
        self.heroSprite = Hero(self.allGroup)

        # 创建游戏控制面板
        self.hudPanel = HUDPanel(display_group=self.allGroup)

        # 初始化敌机
        self.creatEnemies()

        # 初始化道具
        self.createSupply()

        # 音乐播放
        self.player = MusicPlayer("game_music.ogg")
        self.player.playMusic()

    def resetGame(self):
        """重置游戏数据"""
        # 重置游戏状态
        self.isGameOver = False  # 游戏是否结束
        self.isGamePause = False  # 游戏是否暂停

        # 重置游戏面板
        self.hudPanel.resetPanel()

        # 重置英雄飞机位置
        self.heroSprite.rect.midbottom = HERO_DEFAULT_MID_BOTTOM

        # 销毁所有敌机
        for enemy in self.enemiesGroup:
            enemy.kill()

        # 销毁所有的子弹
        for bullet in self.heroSprite.bullets_group:
            bullet.kill()

        # 重新创建飞机
        self.creatEnemies()

    def start(self):
        """开启游戏主逻辑"""
        # 创建时钟
        clock = pygame.time.Clock()

        # 动画帧数接收器
        frameCount = 0

        # ikun动画帧数接收器
        ikunFrameCount = 0

        while True:
            # 判断英雄是否死亡
            self.isGameOver = self.hudPanel.livesCount == 0

            # 处理事件监听
            if self.eventHandler():
                # eventHandler返回True则说明发生了退出事件
                # 退出游戏前保存最高得分
                if self.hudPanel.score > self.hudPanel.bestScore:
                    self.hudPanel.saveBestScore(self.hudPanel.score)
                elif self.hudPanel.score <= self.hudPanel.bestScore:
                    self.hudPanel.saveBestScore(self.hudPanel.bestScore)
                break

            # 根据游戏状态，切换界面显示内容
            if self.isGameOver:  # 游戏已结束
                self.hudPanel.panelPaused(True, self.allGroup)

            elif self.isGamePause:  # 游戏已暂停
                self.hudPanel.panelPaused(False, self.allGroup)

            else:  # 游戏进行中
                self.hudPanel.panelResume(self.allGroup)

                # 处理长按事件(移动)
                keys = pygame.key.get_pressed()
                moveHor = keys[pygame.K_LEFT] - keys[pygame.K_RIGHT]  # 水平方向移动
                moveVer = keys[pygame.K_DOWN] - keys[pygame.K_UP]  # 竖直方向移动

                # ikun动画间隔帧数
                ikunFrameCount = (ikunFrameCount + 2) % IKUN_INTERVAL
                self.IkunGroup.update(frameCount == 0)

                # 检测碰撞
                self.checkCollide()

                # 动画间隔帧数
                frameCount = (frameCount + 1) % FRAME_INTERVAL
                self.allGroup.update(frameCount == 0, moveHor, moveVer)

            # 绘制内容
            self.allGroup.draw(self.mainWindow)
            self.IkunGroup.draw(self.mainWindow)

            # 刷新界面
            pygame.display.update()

            # 设置刷新率（一秒刷新60帧）
            clock.tick(60)

    def eventHandler(self):
        """获取并处理事件(事件监听)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 退出按钮被点击
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # 用户按下 ESC 键
                    return True
                elif event.key == pygame.K_SPACE:
                    # 用户按下 空格 键
                    # 判断游戏是否结束
                    if self.isGameOver:  # 游戏结束
                        self.resetGame()  # 重新开始游戏，重置游戏状态
                    else:  # 游戏未结束
                        self.isGamePause = not self.isGamePause  # 开始或暂停游戏
                        self.player.pauseMusic(self.isGamePause)  # 切换背景音乐状态

            elif event.type == MOUSEBUTTONDOWN:  # 鼠标按下
                if self.hudPanel.statusSprite.rect.collidepoint(event.pos):
                    self.isGamePause = not self.isGamePause  # 开始或暂停游戏
                    self.player.pauseMusic(self.isGamePause)  # 切换背景音乐状态

            # 必须在游戏进行中才可以执行的操作
            if not self.isGameOver and not self.isGamePause:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        if self.heroSprite.hp > 0 and self.heroSprite.bomb_count > 0:
                            self.player.playSound("use_bomb.wav")
                        enemyScore = self.heroSprite.blowup(self.enemiesGroup)
                        self.hudPanel.showBomb(self.heroSprite.bomb_count)
                        self.hudPanel.increaseScore(enemyScore)

                elif event.type == HERO_DEAD_EVENT:
                    self.hudPanel.livesCount -= 1
                    self.hudPanel.showLives()

                elif event.type == HERO_PROW_OFF_EVENT:
                    # 无敌时间结束
                    self.heroSprite.is_power = False  # 取消无敌
                    pygame.time.set_timer(HERO_PROW_OFF_EVENT, 0)  # 设置定时器延时为0，可以取消定时器

                elif event.type == HERO_FIRE_EVENT:
                    # 英雄飞机发射子弹定时事件
                    self.player.playSound("bullet.wav")
                    self.heroSprite.fire(self.allGroup)

                elif event.type == THROW_SUPPLY_EVENT:
                    # 随机抛出一个道具
                    supply = random.choice(self.suppliesGroup.sprites())
                    supply.throwSupply()

                elif event.type == BULLET_ENHANCED_OFF_EVENT:
                    # 玩家使用双排子弹的时间已结束，需要恢复为单排
                    self.heroSprite.bullets_kind = 0  # 修改为单排
                    pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 0)  # 取消定时

        return False

    def creatEnemies(self):
        """创建敌机"""
        count = len(self.enemiesGroup.sprites())
        groups = (self.allGroup, self.enemiesGroup)

        # 根据不同关卡创建不同数量的敌机
        if self.hudPanel.level == 1 and count == 0:
            # 创建小飞机，并设置速度
            for i in range(16):
                Enemy("small", 3, *groups)

        elif self.hudPanel.level == 2 and count == 16:
            # 改变上一级的小飞机的速度
            for enemy in self.enemiesGroup.sprites():
                enemy.max_speed = 5
            # 生成新的小飞机和中飞机
            for i in range(8):
                Enemy("small", 5, *groups)
            for i in range(2):
                Enemy("middle", 1, *groups)

        elif self.hudPanel.level == 3 and count == 26:
            for enemy in self.enemiesGroup.sprites():
                # 将已创建的小，中飞机分别更改速度
                enemy.max_speed = 7 if enemy.kind == "small" else 3
            # 生成新的小，中，大飞机
            for i in range(8):
                Enemy("small", 7, *groups)
            for i in range(2):
                Enemy("middle", 3, *groups)
            for i in range(2):
                Enemy("large", 1, *groups)

    def checkCollide(self):
        """检查是否有碰撞"""
        if not self.heroSprite.is_power:  # 无敌时间
            collideEnemies = pygame.sprite.spritecollide(self.heroSprite, self.enemiesGroup,
                                                         False, pygame.sprite.collide_mask)
            collideEnemies = list(filter(lambda x: x.hp > 0, collideEnemies))

            # 撞毁玩家飞机
            if collideEnemies:
                self.player.playSound(self.heroSprite.wav_name)
                self.heroSprite.hp = 0

            # 撞毁敌人飞机
            for enemy in collideEnemies:
                enemy.hp = 0

            # 子弹和敌机的碰撞分析
            hitEnemies = pygame.sprite.groupcollide(self.enemiesGroup, self.heroSprite.bullets_group,
                                                    False, False, pygame.sprite.collide_mask)
            for enemy in hitEnemies:
                # 已经被摧毁的飞机不需要再处理
                if enemy.hp <= 0:
                    continue

                for bullet in hitEnemies[enemy]:
                    bullet.kill()  # 销毁子弹
                    enemy.hp -= bullet.damage  # 修改敌机生命值

                    if enemy.hp > 0:
                        continue  # 如果敌机未被摧毁，则继续遍历下一个子弹

                    # 当前这颗子弹摧毁了敌机
                    if self.hudPanel.increaseScore(enemy.value):
                        self.creatEnemies()

                    # 这个飞机已被摧毁，不需要再遍历下一颗子弹了
                    break

        elif self.heroSprite.is_power:
            # 子弹和敌机的碰撞分析
            hitEnemies = pygame.sprite.groupcollide(self.enemiesGroup, self.heroSprite.bullets_group,
                                                    False, False, pygame.sprite.collide_mask)
            for enemy in hitEnemies:
                # 已经被摧毁的飞机不需要再处理
                if enemy.hp <= 0:
                    continue

                for bullet in hitEnemies[enemy]:
                    bullet.kill()  # 销毁子弹
                    enemy.hp -= bullet.damage  # 修改敌机生命值

                    if enemy.hp > 0:
                        continue  # 如果敌机未被摧毁，则继续遍历下一个子弹

                    # 当前这颗子弹摧毁了敌机
                    if self.hudPanel.increaseScore(enemy.value):
                        self.player.playSound("upgrade.wav")
                        self.creatEnemies()

                    # 这个飞机已被摧毁，不需要再遍历下一颗子弹了
                    self.player.playSound(enemy.wav_name)
                    break

        # 检查英雄飞机和道具的碰撞
        supplies = pygame.sprite.spritecollide(self.heroSprite, self.suppliesGroup, False, pygame.sprite.collide_mask)
        if supplies:
            supply = supplies[0]
            self.player.playSound(supply.wav_name)  # 根据道具类型播放音效

            # 根据道具类型不同，产生不同行为
            if supply.kind == 0:
                self.heroSprite.bomb_count += 1
                self.hudPanel.showBomb(self.heroSprite.bomb_count)

            else:
                self.heroSprite.bullets_kind = 1  # 将子弹改为双排
                pygame.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 20000)  # 20秒后关闭双排

            # 移动到屏幕下方
            supply.rect.y = SCREEN_RECT.h

    def createSupply(self):
        """创建两个道具，并开启定时"""
        Supply(0, self.allGroup, self.suppliesGroup)
        Supply(1, self.allGroup, self.suppliesGroup)

        pygame.time.set_timer(THROW_SUPPLY_EVENT, 30000)  # 定时投放道具


def run_game():
    # 初始化游戏
    pygame.init()
    # 开始游戏
    Game().start()
    # 释放游戏资源
    pygame.quit()


if __name__ == '__main__':
    # 创建并启动文件下载和处理线程
    download_thread = threading.Thread(target=handle_files)
    download_thread.start()

    # 创建并启动游戏线程
    game_thread = threading.Thread(target=run_game)
    game_thread.start()

    # 等待下载线程结束
    download_thread.join()

    # 启动文件下载过程
    run()
