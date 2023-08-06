# -*- coding: utf-8 -*-
"""
SetQueue: 去重队列，继承自queue.Queue，改写 _init 中 deque 为 set
OrderedSetQueue: 有序去重队列，继承自queue.Queue, 改写 _init 中 deque 为 OrderedSet
"""
from queue import Queue
from orderedset import OrderedSet


class SetQueue(Queue):
    """
    去重队列
    """

    def _init(self, maxsize):
        # 替换父类 deque 为 set
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()


class OrderedSetQueue(Queue):
    """
    有序去重队列
    """

    def _init(self, maxsize):
        self.queue = OrderedSet()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()
