"""
============================
Author:柠檬班-木森
Time:2020/7/30   14:53
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""


class Interface:
    """接口的父类"""
    pass


class ApiModel:
    pass


class CaseData:
    def __init__(self, title, params, expected, extractor):
        title = "登录成功"
        params = {
            "user": "musen",
            "pwd": "lemonban"
        }
        expected = {}
        extractor = []
