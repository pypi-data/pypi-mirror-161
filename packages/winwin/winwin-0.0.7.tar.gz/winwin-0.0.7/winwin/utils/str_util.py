# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 20:23
# @Author  : zbmain

# 常用的类型
NUM = '0-9'
LETTERS = 'a-zA-Z'
NORMAL_CHAR = '!,.?！，。？'
SPECIAL_CHAR = '’"#$%&\'()*+-/;；<=>@★☆〇〖〗、【】＜＞《》“”‘’\\[\\\\]^_`{|}~'
CN_Unicode = '\u4E00-\u9FA5'  # 中文
CN_Unicdoe2 = '\u4E00-\u9FEF'  # 中文2


def clearNull(char: str):
    '''防止爬虫抓到特殊隐藏字符'''
    import re
    return re.sub(
        '[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+',
        '', char)


def lstrip(text, dirty, num=float('inf')):
    """清除字符结尾"""
    if num > 0 and text:
        if text[0] == dirty:
            return lstrip(text[1:], dirty, num - 1)
    return text


def rstrip(text, dirty, num=float('inf')):
    """清除字符结尾"""
    if num > 0 and text:
        if text[-1] == dirty:
            return rstrip(text[:-1], dirty, num - 1)
    return text


def strip(text, dirty, num=float('inf')):
    """清除首尾字符"""
    if num > 0 and text:
        if text[-1] == dirty:
            return lstrip(rstrip(text[:-1], dirty, num - 1), dirty, num)
    return text


def split(text, split_char: str = ';', prefix_char: str = '', suffix_char: str = '') -> list:
    """
    切分(字符串/列表)

    :param text: 切分对象[str;list]
    :param split_char: text为str时的切分符号
    :param prefix_char: 切分后的前缀字符
    :param suffix_char: 切分后的后缀字符
    :return: 切分后的列表
    """
    queue = type(text) is list and text or strip(text, split_char).split(split_char)
    return [prefix_char + char + suffix_char for char in queue if char]


def remove_invalid_words(x: str):
    return filter(lambda y: y.strip(), map(lambda z: z.strip(), x))


def is_number(s):
    if s:
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
    return False


if __name__ == '__main__':
    print(split('a;b;;c', ';', '_', '.bin'))
    print(split(['a', 'b', 'c'], ';', '_', '.bin'))
    print('a;b;c'.split(';'))
    print(list(remove_invalid_words('a\t \u0020b')))
    print(is_number('123'))
    print(is_number('abc'))
    print(strip(';;;123;;;;', ';', 1))
