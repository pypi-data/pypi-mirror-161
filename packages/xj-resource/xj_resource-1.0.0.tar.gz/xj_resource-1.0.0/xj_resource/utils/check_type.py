# -*- encoding:utf-8 -*-

class CheckType:
    # 判断是否是数字，包括浮点型
    @staticmethod
    def is_number(s):
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








