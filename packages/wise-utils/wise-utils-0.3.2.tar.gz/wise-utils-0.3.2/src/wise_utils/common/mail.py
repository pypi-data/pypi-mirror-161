# -*- coding: utf-8 -*-
import yagmail


class UtilMail(object):
    def __init__(self, user, password, host, port):
        self.__yag = yagmail.SMTP(user=user, password=password, host=host, port=port)

    def send(self, to, subject, contents: list, cc=None, attachments=None):
        """发送"""
        self.__yag.send(to=to, subject=subject, contents=contents, cc=cc, attachments=attachments)
