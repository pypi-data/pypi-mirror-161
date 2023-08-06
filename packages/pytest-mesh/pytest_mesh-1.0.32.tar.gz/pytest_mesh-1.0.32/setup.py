#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
pytest_mesh 打包文件
@author:zhaojiajun
@file:setup.py
@time:2022/07/13
"""

from setuptools import setup, find_packages

__name__ = 'pytest_mesh'
__version__ = '1.0.32'

setup(
    name=__name__,
    version=__version__,
    author="zhaojiajun",
    author_email='zhaojiajun@baicizhan.com',
    description='pytest_mesh插件',
    packages=[
        'pytest_mesh',
        'pytest_mesh.allure.bin',
        'pytest_mesh.allure.config',
        'pytest_mesh.allure.lib',
        "pytest_mesh.allure.lib.config",
        "pytest_mesh.allure.plugins",
        "pytest_mesh.allure.plugins.behaviors-plugin",
        "pytest_mesh.allure.plugins.behaviors-plugin.static",
        "pytest_mesh.allure.plugins.custom-logo-plugin",
        "pytest_mesh.allure.plugins.custom-logo-plugin.static",
        "pytest_mesh.allure.plugins.jira-plugin",
        "pytest_mesh.allure.plugins.jira-plugin.lib",
        "pytest_mesh.allure.plugins.junit-xml-plugin",
        "pytest_mesh.allure.plugins.packages-plugin",
        "pytest_mesh.allure.plugins.packages-plugin.static",
        "pytest_mesh.allure.plugins.screen-diff-plugin",
        "pytest_mesh.allure.plugins.screen-diff-plugin.static",
        "pytest_mesh.allure.plugins.trx-plugin",
        "pytest_mesh.allure.plugins.xctest-plugin",
        "pytest_mesh.allure.plugins.xctest-plugin.lib",
        "pytest_mesh.allure.plugins.xray-plugin",
        "pytest_mesh.allure.plugins.xray-plugin.lib",
        "pytest_mesh.allure.plugins.xunit-xml-plugin"
    ],
    package_dir={"": "src"},
    # 依赖的资源文件
    include_package_data=True,
    package_data={
        "pytest_mesh.allure.bin": ['*'],
        "pytest_mesh.allure.config": ['*'],
        "pytest_mesh.allure.lib": ['*'],
        "pytest_mesh.allure.lib.config": ['*'],
        "pytest_mesh.allure.plugins": ['*'],
        "pytest_mesh.allure.plugins.behaviors-plugin": ['*'],
        "pytest_mesh.allure.plugins.behaviors-plugin.static": ['*'],
        "pytest_mesh.allure.plugins.custom-logo-plugin": ['*'],
        "pytest_mesh.allure.plugins.custom-logo-plugin.static": ['*'],
        "pytest_mesh.allure.plugins.jira-plugin": ['*'],
        "pytest_mesh.allure.plugins.jira-plugin.lib": ['*'],
        "pytest_mesh.allure.plugins.junit-xml-plugin": ['*'],
        "pytest_mesh.allure.plugins.packages-plugin": ['*'],
        "pytest_mesh.allure.plugins.packages-plugin.static": ['*'],
        "pytest_mesh.allure.plugins.screen-diff-plugin": ['*'],
        "pytest_mesh.allure.plugins.screen-diff-plugin.static": ['*'],
        "pytest_mesh.allure.plugins.trx-plugin": ['*'],
        "pytest_mesh.allure.plugins.xctest-plugin": ['*'],
        "pytest_mesh.allure.plugins.xctest-plugin.lib": ['*'],
        "pytest_mesh.allure.plugins.xray-plugin": ['*'],
        "pytest_mesh.allure.plugins.xray-plugin.lib": ['*'],
        "pytest_mesh.allure.plugins.xunit-xml-plugin": ['*']
    },
    # 需要安装的依赖
    install_requires=[
        'autodoraemon==1.0.5',
        'pytest==7.1.2',
        'allure-pytest==2.9.45',
        'SQLAlchemy==1.4.39'
    ],
    entry_points={
        'pytest11': [
            'pytest-mesh = pytest_mesh.main',
        ]
    }
)

if __name__ == '__main__':
    pass
