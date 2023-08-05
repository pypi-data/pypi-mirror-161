#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
pytest_mesh 插件
完成和mesh的交互

@author:zhaojiajun
@file:main.py
@time:2022/07/13
"""
import pytest
import json
import os
import logging
import site
from . import db
from urllib.parse import quote_plus
from auto_doraemon.util.file_util import write_file, read_file
from auto_doraemon.util.time_util import get_current_time

log = logging.getLogger(__name__)

global is_collect_only  # 是否只是收集测试用例
is_collect_only = False
global test_summary  # 测试结果概要信息
global test_methods  # 需要执行的测试方法list


@pytest.fixture
def mysql(pytestconfig):
    log.info('初始化数据库连接')
    key_list = pytestconfig.inicfg.keys()
    if 'mysql_server' not in key_list \
            or 'mysql_user' not in key_list \
            or 'mysql_password' not in key_list \
            or 'mysql_port' not in key_list \
            or 'mysql_db' not in key_list:
        log.info('数据库配置不正确，请确保在pytest.ini文件中设置mysql_server,mysql_user,mysql_password,mysql_port,mysql_db')
        return None
    mysql = db.MySqlDB(server=pytestconfig.inicfg["mysql_server"], port=pytestconfig.inicfg["mysql_port"],
                       user=pytestconfig.inicfg["mysql_user"],
                       password=quote_plus(pytestconfig.inicfg["mysql_password"]),
                       db=pytestconfig.inicfg["mysql_db"])
    # 将当前测试进程中数据库的管理对象添加到db的engine_dict字典中
    # 后续clickhouse或者redis相关的管理对象也需要添加到此字典中
    db.__add_engine("mysql", mysql)
    return mysql


@pytest.fixture
def lane(pytestconfig):
    """
    泳道
    :param pytestconfig:
    :return:
    """
    return pytestconfig.getoption('lane')


@pytest.fixture
def notify(pytestconfig):
    """
    是否通知
    :param pytestconfig:
    :return:
    """
    return pytestconfig.getoption('notify')


def get_test_methods(file_path: str):
    """
    根据file_path中内容找到所有需要测试的方法
    :param file_path:
    :return:
    """
    content = read_file(file_path)
    content_json = json.loads(content)
    path_list = []
    for tmp in content_json:
        path_list.append(tmp['path'])
    return path_list


@pytest.mark.optionalhook
def pytest_addoption(parser, pluginmanager):
    """
    给pytest 增加自定义参数
    :param parser:
    :param pluginmanager:
    :return:
    """
    parser.addoption("--file", action="store",
                     default="None",
                     help="将自定义命令行参数 ’--file' 添加到 pytest 配置中")
    parser.addoption("--lane", action="store",
                     default='main',
                     help="将自定义命令行参数 ’--lane' 添加到 pytest 配置中")
    parser.addoption("--notify", action="store",
                     default=0,
                     help="将自定义命令行参数 ’--notify' 添加到 pytest 配置中")


@pytest.mark.optionalhook
def pytest_cmdline_preparse(config, args):
    """
    遍历--file 对应的文件，提取出需要执行的测试方法
    :param config:
    :param args:
    :return:
    """
    # 追加 --alluredir 和 --clean-alluredir 命令
    # 将allure的指令收敛于pytest-mesh内部
    args.append('--alluredir=./report_data')
    args.append('--clean-alluredir')
    config.known_args_namespace.allure_report_dir = './report_data'
    for index, value in enumerate(args):
        if '--file' in value:
            path = value.split('=')[1]
            global test_methods
            test_methods = get_test_methods(path)
            break
        if '--collect-only' in value:
            global is_collect_only
            is_collect_only = True
            break


@pytest.mark.optionalhook
def pytest_collection_finish(session):
    """
    过滤收集测试item,只保留指定需要进行测试的方法
    :param session:
    :return:
    """
    if not is_collect_only:
        global test_methods
        new_items = []
        for item in session.items:
            # 调整node_id，避免参数化影响
            path_list = item.nodeid.split("::")
            path_list[len(path_list) - 1] = item.originalname
            path = '::'.join(path_list)
            if path in test_methods:
                new_items.append(item)
        session.items = new_items


@pytest.mark.optionalhook
def pytest_collection_modifyitems(config, items):
    all_test_methods_list = []
    already_add_methods = []
    for item in items:
        module = item.location[0]
        path = item.nodeid
        method = item.location[2]
        original_name = item.originalname
        # 当测试方法参数化时，需要对method和path进行单独调整
        # 调整method信息
        method_list = method.split('.')
        method_list[len(method_list) - 1] = original_name
        method = '.'.join(method_list)
        # 调整path信息
        path_list = path.split("::")
        path_list[len(path_list) - 1] = original_name
        path = '::'.join(path_list)
        # 获取测试方法描述信息
        tmp_desc_list = list(
            filter(lambda tmp_mark: tmp_mark.name == 'allure_label' and tmp_mark.kwargs[
                'label_type'] == 'story', item.own_markers))
        # TODO:判断此测试方法是否已经添加，如果已经添加就不再重复添加
        if method not in already_add_methods:
            already_add_methods.append(method)
            all_test_methods_list.append({'module': module, 'method': method, 'path': path,
                                          'desc': tmp_desc_list[0].args[0] if tmp_desc_list else "未知"})
    json_str = json.dumps(all_test_methods_list, ensure_ascii=False, indent=4)
    # 将所有发现的的测试方法及相关信息写入到当前工程目录下的all_methods.json中
    write_file(os.getcwd(), 'all_methods.json', json_str)


@pytest.mark.optionalhook
def pytest_sessionstart(session):
    """
    测试流程的会话启动
    :param session: 测试会话
    :return:
    """
    log.info('{} session start'.format(session.name))
    global test_summary
    test_summary = {
        'start_time': get_current_time("%Y-%m-%d %H:%M:%S")
    }


@pytest.mark.optionalhook
def pytest_sessionfinish(session, exitstatus):
    """
    测试流程的会话结束
    :param session:
    :param exitstatus:
    :return:
    """
    log.info('{} session finish'.format(session.name))
    # 生成测试概要数据文件
    if not is_collect_only:
        log.info('start to generate test result summary file')
        global test_summary
        terminal_reporter = session.config.pluginmanager.get_plugin('terminalreporter')
        stats_keys = terminal_reporter.stats.keys()
        test_summary['testcase_pass'] = len(terminal_reporter.stats.get('passed')) if 'passed' in stats_keys else 0
        test_summary['testcase_fail'] = len(terminal_reporter.stats.get('failed')) if 'failed' in stats_keys else 0
        test_summary['testcase_skip'] = len(terminal_reporter.stats.get('skipped')) if 'skipped' in stats_keys else 0
        test_summary['end_time'] = get_current_time("%Y-%m-%d %H:%M:%S")
        test_summary['total_test_case'] = session.testscollected
        write_file(os.getcwd(), 'test_summary.json', json.dumps(test_summary, indent=4))
        log.info('start to generate allure report')
        allure_path = os.path.join(site.getsitepackages()[0], 'pytest_mesh', 'allure', 'bin', 'allure')
        allure_command = '{} generate {} -o {} --clean'.format(allure_path, './report_data', './report_html')
        log.info('allure_command', allure_command)
        os.system(allure_command)


@pytest.mark.optionalhook
def pytest_runtest_setup(item):
    log.info('test method {} setup'.format(item.name))


@pytest.mark.optionalhook
def pytest_runtest_call(item):
    log.info('test method {} call to run'.format(item.name))


@pytest.mark.optionalhook
def pytest_runtest_teardown(item):
    log.info('test method {} teardown'.format(item.name))


if __name__ == '__main__':
    pass
