# -*- coding: utf-8 -*-
# @Time    : 2022-07-22 18:20
# @Author  : zbmain

import time

import pandas


def delay(second: int):
    time.sleep(second)

    def wrapper(func):
        def inner(*args, **kwargs):
            ret = func(*args, **kwargs)
            return ret

        return inner

    return wrapper


def view_df(df: pandas.DataFrame, head_num: int = 5, tail_num: int = 5, comment: str = 'DataFrame'):
    print('%s row_size:%d' % (comment, len(df.index)))
    return df.head(head_num).append(df.tail(tail_num))


import warnings


def warning_ignored():
    """关闭一些警告(不推荐)"""
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)


def set_seed(seed: int = 1990):
    import numpy, random
    random.seed(seed)
    numpy.random.seed(seed)
    try:
        import tensorflow
        tensorflow.random.set_seed(seed)
        tensorflow.set_random_seed(seed)
    except:
        pass

    try:
        import torch
        torch.manual_seed(seed)  # cpu
        torch.cuda.manual_seed(seed)  # gpu
        torch.cuda.manual_seed_all(seed)  # all gpu
    except:
        pass
