# -*- coding: utf-8 -*-
"""
重试机制，此装饰器只适用于装饰类中的方法，并且，调用的也是类中的方法，关键处在于：是否接收并传递self
"""
import time

from inspect import isfunction


def __before_sleep(*args, **kwargs):
    pass


def __after_sleep(*args, **kwargs):
    pass


def __retry_error_callback(*args, **kwargs):
    pass


def retry(retry_times=5, current_times=0, wait=1, before_sleep=__before_sleep, after_sleep=__after_sleep, retry_error_callback=__retry_error_callback, remark=""):
    """
    装饰器实现重试机制
    :param retry_times: 重试次数：默认5次，-1代表一直重试
    :param current_times: 当前重试的次数
    :param wait: 每次重试的时间间隔
    :param before_sleep: 重试睡眠前调用的函数
    :param after_sleep: 重试睡眠后调用的函数
    :param retry_error_callback: 重试结束仍然失败时的回调函数
    :param remark: 备注
    :return:
    """

    def catch_exception(func):
        def wrapper(self, *args, **kwargs):
            nonlocal retry_times, current_times
            try:
                # 调用func
                return func(self, *args, **kwargs)
            except Exception as e:
                current_times += 1
                # 睡眠前调用
                if isfunction(before_sleep):
                    before_sleep(self, current_times=current_times, remark=remark)

                # 重试间隔
                time.sleep(wait)

                # 睡眠后调用
                if isfunction(after_sleep):
                    after_sleep(self, current_times=current_times, remark=remark)

                if retry_times == -1:
                    return wrapper(self, *args, **kwargs)
                elif current_times > retry_times:
                    if isfunction(retry_error_callback):
                        # 重试结束，执行回调函数
                        return retry_error_callback(self, retry_times=retry_times, remark=remark)
                    else:
                        # 没有指定回调函数时，弹出错误
                        raise e
                else:
                    current_times += 1
                    return wrapper(self, *args, **kwargs)

        # 设置current_times参数值
        def set_current_times(value):
            nonlocal current_times
            current_times = value

        wrapper.set_current_times = set_current_times
        return wrapper

    return catch_exception
