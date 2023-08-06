# -*- coding: utf-8 -*-
"""
操作FTP服务器
目前仅支持下载和删除
"""
import os
import ftplib


def connect_ftp_server(func):
    def wrapper(self, *args, **kwargs):
        try:
            self.ftp.cwd("/")
        except:
            self.ftp = self.ftp_connect()
        return func(self, *args, **kwargs)

    return wrapper


class FtpTool(object):

    def __init__(self, ip, port, username, password):
        self.ftp_server = ip  # ftp主机IP
        self.port = port  # ftp端口
        self.username = username  # 登陆用户名
        self.password = password  # 登陆密码
        self.ftp = self.ftp_connect()

    def ftp_connect(self):
        """ftp连接"""
        ftp = ftplib.FTP()
        try:
            ftp.connect(self.ftp_server, self.port)
            ftp.login(self.username, self.password)
        except:
            raise IOError('FTP login failed!!!')
        else:
            print(ftp.getwelcome())
            return ftp

    @connect_ftp_server
    def upload_file(self, remote_path, local_path):
        """
        上传文件
        """
        self.ftp.cwd(remote_path)
        buf_size = 1024 * 1024
        with open(local_path, "rb") as f:
            self.ftp.storbinary('STOR %s' % os.path.basename(local_path), f, buf_size)  # 上传文件到ftp服务器
        return True

    @connect_ftp_server
    def download_file(self, remote_path, local_path):
        """单个文件下载到本地"""
        with open(local_path, 'wb') as file_handle:
            self.ftp.retrbinary(f"RETR {remote_path}", file_handle.write)
            print(f"下载至: {local_path}")
        return True

    @connect_ftp_server
    def download_files(self, remote_path, local_path):
        """下载整个目录下的文件,包括子目录文件"""
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        self.ftp.cwd(remote_path)

        for i, file_name in enumerate(self.ftp.nlst()):
            if not file_name.endswith(".zip"):
                continue
            ftp_path = os.path.join(remote_path, file_name)
            local = os.path.join(local_path, file_name)

            if self.__is_filedir(file_name=file_name):  # 判断是否为子目录
                if not os.path.exists(local):
                    os.makedirs(local)
                self.download_files(remote_path=ftp_path, local_path=local)
            else:
                self.download_file(remote_path=ftp_path, local_path=local)
        self.ftp.cwd('..')
        return True

    @connect_ftp_server
    def move_file(self, from_path, to_path):
        """移动文件"""
        self.ftp.rename(from_path, to_path)
        return True

    @connect_ftp_server
    def delete_file(self, remote_file_path):
        """删除文件夹中的所有文件"""
        try:
            self.ftp.delete(remote_file_path)
            print(f"{remote_file_path} 删除成功")
        except Exception as e:
            print(e)

    @connect_ftp_server
    def delete_files(self, remote_path):
        """清空文件夹"""
        self.ftp.cwd(remote_path)
        for file_name in self.ftp.nlst():
            if not file_name.endswith(".zip"):
                continue
            if self.__is_filedir(file_name=file_name):  # 判断是否为子目录
                self.delete_files(file_name)
            else:
                self.ftp.delete(file_name)

    @connect_ftp_server
    def ftp_disconnect(self):
        """退出FTP连接"""
        self.ftp.quit()

    def __is_filedir(self, file_name):
        """
        判断是否是文件夹
        :param file_name: 文件名/文件夹名
        :return:返回字符串“File”为文件，“Dir”问文件夹，“Unknow”为无法识别
        """
        rec = ""
        try:
            rec = self.ftp.cwd(file_name)  # 需要判断的元素
            self.ftp.cwd("..")  # 如果能通过路劲打开必为文件夹，在此返回上一级
        except Exception as e:
            rec = e  # 不能通过路劲打开必为文件，抓取其错误信息
        finally:
            if "550 Failed to change directory" in str(rec):
                return False
            elif "Directory successfully changed." in str(rec):
                return True
            else:
                return False
