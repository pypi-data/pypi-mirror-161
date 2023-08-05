# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 09:42
# @Author  : zbmain
"""
HOME                -> 环境变量目录
├── MODULE_HOME     -> 模型
├── DATA_HOME       -> 数据集
├── CACHE_HOME      -> 缓存目录
├── CONF_HOME       -> 配置目录
├── TMP_HOME        -> 临时文件
├── LOG_HOME        -> 日志
├── SOURCES_HOME    -> 代码
└── RESOURCES_HOME  -> 资源
"""
import os

HUB_HOME_KEY = 'WINWIN_HUB_HOME'
"""WINWIN_HOME - 环境变量Key"""
HUB_HOME_DIR = '.winwin_hub'
"""WINWIN_HOME - 本地目录名"""


def _get_user_home():
    return os.path.expanduser('~')


def _get_hub_home():
    if HUB_HOME_KEY in os.environ:
        home_path = os.environ[HUB_HOME_KEY]
        if os.path.exists(home_path):
            if os.path.isdir(home_path):
                return home_path
            else:
                raise RuntimeError('The environment variable WINWIN_HOME {} is not a directory.'.format(home_path))
        else:
            return home_path
    os.environ[HUB_HOME_KEY] = os.path.join(_get_user_home(), HUB_HOME_DIR)
    return os.environ[HUB_HOME_KEY]


def _get_sub_home(directory):
    home = os.path.join(_get_hub_home(), directory)
    os.makedirs(home, exist_ok=True)
    return home


USER_HOME = _get_user_home()
HUB_HOME = _get_hub_home()
MODULE_HOME = _get_sub_home('modules')
DATA_HOME = _get_sub_home('dataset')
CACHE_HOME = _get_sub_home('cache')
CONF_HOME = _get_sub_home('conf')
TMP_HOME = _get_sub_home('tmp')
LOG_HOME = _get_sub_home('log')
SOURCES_HOME = _get_sub_home('sources')
RESOURCES_HOME = _get_sub_home('resources')
