"""
============================
Author:柠檬班-木森
Time:2020/7/28   17:12
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
import os
from shutil import copytree
from TestAuto.core.handle_path import api_templates, web_templates


class ProjectManage(object):
    @classmethod
    def create_api(cls, name):
        print("正在创建api自动化项目")
        print("打印路径：", api_templates)
        print("打印getcwd:",os.getcwd())
        print("__file__",__file__)
        copytree(api_templates, os.path.join(".", name))

    @classmethod
    def create_web(cls, name):
        print("正在创建api自动化项目")
        copytree(web_templates, os.path.join(".", name))
