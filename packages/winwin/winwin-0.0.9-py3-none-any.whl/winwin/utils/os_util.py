# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 21:09
# @Author  : zbmain
import logging
import os
import shutil
import time

HOME_PATH = os.path.expanduser('~')
"""用户目录"""
CURRENT_ROOT_PATH = os.path.abspath('.')
"""项目跟目录"""


def get_suffix(path):
    """路径后缀"""
    return os.path.splitext(path)[1]


def dir2list_with_suffix(dirpath: str, suffix=('.xlsx', '.csv', '.tsv'), ignoring_hidden_file: bool = True):
    return [os.path.join(dirpath, path) for path in os.listdir(dirpath) if
            get_suffix(path) in suffix and (path[0] != '.' if ignoring_hidden_file else True)]


def mkdir(dirpath: str):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


def makedirs(dirpath: str):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def del_dirs(path: str, only_sub_file: bool = True):
    """
    清空目录

    :param path: 待清空的目录
    :param only_sub_file: 只清空子目录和子文件（保留原目录）
    :return:
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            if only_sub_file:
                del_list = os.listdir(path)
                for f in del_list:
                    file_path = os.path.join(path, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            else:
                shutil.rmtree(path)
        else:
            os.remove(path)


def parse_filepath(filepath):
    filepath, fullflname = os.path.split(filepath)
    fname, ext = os.path.splitext(fullflname)
    return filepath, fname, ext


def get_modify_time(file: str, format: str = '%Y/%m/%d %H:%M:%S'):
    """文件名的后四位（是日期）"""
    return time.strftime(format, time.localtime(os.stat(file).st_mtime))


def get_create_time(file: str, format: str = '%Y/%m/%d %H:%M:%S'):
    """文件名的后四位（是日期）"""
    return time.strftime(format, time.localtime(os.stat(file).st_ctime))


def network_state():
    '''ping 网络状态'''
    logging.info('Check Network...')
    result = os.system(u"ping -c2 baidu.com > /dev/null 2>&1")  # 都丢弃，防止输出到控制台
    return result == 0


if __name__ == '__main__':
    print(parse_filepath('/home/deploy/tmp/'))
    print(get_modify_time('/home/deploy/tmp/'))
    print(get_create_time('/home/deploy/tmp/'))
    print(dir2list_with_suffix('/home/deploy/tmp/', ignoring_hidden_file=False))
    del_dirs('/home/deploy/tmp/tmps/', only_sub_file=True)
    print(HOME_PATH)
    print(CURRENT_ROOT_PATH)
