import time
import random


class MockData(object):
    """随机数据+当前时间数据"""

    # -----------------------------随机数据-------------------------------
    @staticmethod
    def no_repeat_word(head='词语'):
        """不重复的词语"""
        return head + str(int(time.time()))

    @staticmethod
    def random_word_list(length=3):
        """随机词语列表"""
        word_list = []
        for i in range(length):
            tmp_str = ''.join([chr(random.randint(0x4e00, 0x9fbf)) for i in range(2)])
            word_list.append(tmp_str)
        return word_list

    @staticmethod
    def random_phone_number():
        """随机手机号"""
        phone_head_dx = ['133', '153', '180', '181', '189', '177', '173', '149']
        phone_head_lt = ['130', '131', '132', '155', '156', '145', '185', '186', '176', '175']
        phone_head_yd = ['134', '135', '136', '137', '138', '139', '150', '151', '152', '157', '158', '159', '182', '183', '184', '187', '188', '147', '178']
        phone_number = random.choice(phone_head_dx + phone_head_lt + phone_head_yd) + str(int(time.time()))[:8]
        return phone_number

    @staticmethod
    def random_number(start=1, end=1000):
        """随机数"""
        return random.randint(start, end)

    @staticmethod
    def now_timestamp(length=None) -> str:
        """获取当前时间戳"""
        timestamp = str(int(time.time()))
        if length is None:
            return timestamp
        else:
            return timestamp.ljust(length, '0')

    @staticmethod
    def now_date(_format="%Y-%m-%d"):
        """获取当前日期"""
        return time.strftime(_format)

    @staticmethod
    def now_time(_format="%Y-%m-%d %H:%M:%S"):
        """获取当前时间"""
        return time.strftime(_format)


# 初始化
mock_data = MockData()








