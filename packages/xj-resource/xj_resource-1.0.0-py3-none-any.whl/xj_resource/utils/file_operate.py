# -*- encoding:utf-8 -*-
import os


class FileOperate:

    # 如果没有目录，则创建目录
    @staticmethod
    def make_dir(folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return True







