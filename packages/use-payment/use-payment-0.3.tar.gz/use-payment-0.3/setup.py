from distutils.core import setup

# from os import path as os_path
#
# this_directory = os_path.abspath(os_path.dirname(__file__))
#
#
# def read_file(filename):
#     with open(os_path.join(this_directory, filename)) as f:
#         long_description = f.read()
#         return long_description
from setuptools import Extension, dist, find_packages, setup

setup(
    name="use-payment",
    version="0.3",
    author="Ryan",
    packages=find_packages(),  # 所有带__init__的文件夹
    author_email="604729765@qq.com",
    url="https://www.leetab.com",
    description="支持支付宝和微信支付的支付模块",
    install_requires=["cryptography>=37.0.4"],
    long_description=open("README.rst", encoding="utf-8").read(),  # README.rst必须大写
)

# python setup.py sdist
# twine upload dist/*
