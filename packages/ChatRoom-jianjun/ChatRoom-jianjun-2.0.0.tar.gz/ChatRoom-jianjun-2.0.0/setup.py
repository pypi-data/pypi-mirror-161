#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name = 'ChatRoom-jianjun',
    version = '2.0.0',
    author = 'jianjun',
    author_email = '910667956@qq.com',
    url = 'https://github.com/EVA-JianJun/ChatRoom',
    description = u'Python 聊天室!',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = ["ChatRoom"],
    install_requires = [
        "rsa>=4.0",
        "bcrypt>=3.2.0",
        "psutil>=5.7.0",
        "tqdm>=4.44.1",
        "Mconfig>=1.1.4",
        "ttkbootstrap>=1.9.0",
        "yagmail>=0.15.280"
    ],
    entry_points={
        'console_scripts': [
            'room=ChatRoom:_RunRoom'
        ],
    },
)