# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/24 20:58
"""
import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# 生成密钥函数
def generate_key(password, salt):
    """
    使用PBKDF2HMAC算法生成密钥。

    :param password: 用户密码的字节对象
    :param salt: 用于密钥生成的盐
    :return: 派生出的密钥
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # 使用SHA256哈希算法
        length=32,  # 生成的密钥长度为32字节
        salt=salt,  # 使用提供的盐
        iterations=100000,  # 进行100000次迭代
        backend=default_backend()  # 使用默认的加密后端
    )
    return kdf.derive(password)  # 返回派生出的密钥


# 加密函数
def encrypt(data, en_password):
    """
    使用AES算法加密数据。

    :param data: 需要加密的数据
    :param en_password: 用于生成密钥的加密密码（base64编码）
    :return: 加密后的数据（base64编码）
    """
    password = base64.b64decode(en_password)  # 解码密码
    salt = os.urandom(16)  # 生成一个16字节的随机盐
    key = generate_key(password, salt)  # 使用密码和盐生成密钥
    iv = os.urandom(16)  # 生成一个16字节的随机初始化向量（IV）
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())  # 创建AES密码对象，使用CBC模式
    encryptor = cipher.encryptor()  # 创建加密器
    padder = padding.PKCS7(algorithms.AES.block_size).padder()  # 创建填充器，使用PKCS7填充
    padded_data = padder.update(data) + padder.finalize()  # 对数据进行填充
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()  # 加密填充后的数据
    return base64.b64encode(salt + iv + encrypted_data)  # 返回加密后的数据，并进行base64编码


# 解密函数
def decrypt(encrypted_data, en_password):
    """
    使用AES算法解密数据。

    :param encrypted_data: 需要解密的数据（base64编码）
    :param en_password: 用于生成密钥的加密密码（base64编码）
    :return: 解密后的数据
    """
    password = base64.b64decode(en_password)  # 解码密码
    encrypted_data = base64.b64decode(encrypted_data)  # 解码加密数据
    salt = encrypted_data[:16]  # 提取前16字节作为盐
    iv = encrypted_data[16:32]  # 提取接下来的16字节作为初始化向量（IV）
    encrypted_data = encrypted_data[32:]  # 剩下的为实际的加密数据
    key = generate_key(password, salt)  # 使用密码和盐生成密钥
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())  # 创建AES密码对象，使用CBC模式
    decryptor = cipher.decryptor()  # 创建解密器
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()  # 解密数据
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()  # 创建去填充器，使用PKCS7填充
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()  # 去除填充
    return decrypted_data  # 返回解密后的数据
