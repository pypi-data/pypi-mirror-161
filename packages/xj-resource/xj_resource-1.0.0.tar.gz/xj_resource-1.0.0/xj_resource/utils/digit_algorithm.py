# -*- encoding:utf-8 -*-
import time, os
from datetime import datetime
from hashlib import md5


class DigitAlgorithm:

    @staticmethod
    # 生成交易号：2位数（当前年份后2位数字）+8位数（当前时间戳去头2位）+6位数（用户名 经过hash crc16生成的 4位十六进制 转成5位数 然后头为补0）
    def make_unicode_16(salt=''):
        # 当前时间戳
        date_time = time.localtime(time.time())
        # 截取第3位到第4位
        year_code = str(date_time.tm_year)[2:4]

        # 当前时间戳
        timestamp = str(int(time.time()))
        # 截取第3位到第10位
        timestamp_code = timestamp[2:10]

        # 十六进制校验码
        crc_hex = Jt.crc16(salt) if salt else '0'
        # 十六进制转十进制
        crc_int = int(crc_hex, 16)
        # 头位补0
        crc_code = str('000000' + str(crc_int))[-6:]
        unicode = year_code + timestamp_code + crc_code

        return unicode

    # 生成日期yyyymmdd（8位）+时间（6位）hhmmss+毫秒（3位）=17位日期时间型数字
    @staticmethod
    def make_datetime_17():
        # 8位数+6+3=17位数
        t = time
        ms = int((t.time() - int(t.time()))*1000)
        return t.strftime('%Y%m%d%H%M%S',) + str(ms)

    @staticmethod
    def make_datetime_14():
        return time.strftime('%Y%m%d%H%M%S', )

    # crc16
    @staticmethod
    def crc16(x):
        a = 0xFFFF
        b = 0xA001
        for byte in x:
            a ^= ord(byte)
            for i in range(8):
                last = a % 2
                a >>= 1
                if last == 1:
                    a ^= b
        s = hex(a).upper()

        return s[2:6]

    # 文件生成md5
    @staticmethod
    def make_file_md5(file):
        if not os.path.exists(file):
            return None
        f = open(file, "rb")
        m = md5()
        m.update(f.read())
        f.close()
        result = m.hexdigest()
        return result







