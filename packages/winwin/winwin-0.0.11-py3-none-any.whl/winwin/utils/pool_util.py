# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 20:41
# @Author  : zbmain
class ObjectPool(object):
    def __init__(self, Cls):
        super(ObjectPool, self).__init__()
        self.Cls = Cls
        self.__storage__ = {}

    def _put(self, obj: object, key=None, froce=True):
        key = key or (hasattr(obj, 'name') and obj.__getattribute__('name')) or ''
        if froce or self.__storage__.get(key) is not None:
            self.__storage__[key] = obj

    def set(self, key, *args, **kwargs):
        _obj = self.__storage__.get(key)
        if _obj:
            _obj.__init__(*args, **kwargs)
        else:
            _obj = self.Cls(*args, **kwargs)
            self._put(_obj, key)
        return _obj

    def get(self, key, *args, **kwargs):
        """
        pool get instance of Cls

        :param key: unique key
        :param args: class args param
        :param kwargs: class kwargs param
        :return: unique key instance
        """
        return self.set(key, *args, **kwargs)


import threading


def Singleton(cls):
    '''普通单例装饰器，不支持多线程 @Singleton'''
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


class SingletonType(type):
    '''元类单例模式，支持多线程 Class(metaclass=SingletonType])'''
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


if __name__ == '__main__':
    class A:
        def __init__(self, name=None):
            self.name = name


    pool = ObjectPool(A)
    print(pool.get('win', 'winwin').name)
    print(pool.__storage__.keys())
    print(pool.get('win', 'winers').name)
    print(pool.__storage__.keys())
    print('ok')
