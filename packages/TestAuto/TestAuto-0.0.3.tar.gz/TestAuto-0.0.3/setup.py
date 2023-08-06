"""
============================
Author:柠檬班-木森
Time:2020/7/16   16:20
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
from setuptools import setup, find_packages

with open("readme.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setup(
    name='TestAuto',
    version='0.0.3',
    author='MuSen',
    author_email='musen_nmb@qq.com',
    url='https://github.com/musen123/TestAuto',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["Jinja2==2.10.1"],
    packages=find_packages(),
    package_data={
        "": ["*.html",'*.md'],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    # 安装时生成脚本命令行脚本文件
    entry_points={
        "console_scripts": [
            "testauto = TestAuto.management:execute_from_command_line",
        ],
    }
)
