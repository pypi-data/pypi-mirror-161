#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
数据库相关

@author:zhaojiajun
@file:db.py
@time:2022/07/26
"""
import sqlalchemy
from sqlalchemy.orm import Session
import logging

log = logging.getLogger(__name__)

global engine_list
engine_list = []


class MySqlDB:
    """
    通过SQLAlchemy 维护与mysql数据库的连接
    """

    def __init__(self, server: str, port: str, user: str, password: str, db: str):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.engine = self.__init_engine()

    def __init_engine(self):
        """
        初始化目标数据库的连接

        :return:
        """
        log.info('初始化mysql数据库连接.')
        url = f'mysql+pymysql://{self.user}:{self.password}@{self.server}:{self.port}/{self.db}'
        log.info('mysql连接地址：{}'.format(url))
        engine = sqlalchemy.create_engine(url, echo=True, future=True)
        log.info('mysql数据库连接成功.')
        return engine

    def execute(self, sql: str):
        """
        执行sql语句

        :param sql:语句
        :return:
        """
        with Session(self.engine) as session:
            result = session.execute(sql)
            return result


def __get_engine(type):
    """
    获取目标数据库连接的engine
    :param type:
    :return:
    """
    target_engine_list = list(filter(lambda item: item['type'] == 'mysql', engine_list))
    if not target_engine_list or len(target_engine_list) > 1:
        raise Exception('目标类型{}的数据库连接对象异常'.format(type))
    return target_engine_list[0]


def __add_engine(type, engine):
    """
    添加目标数据库连接的engine
    :param type:
    :param engine:
    :return:
    """
    target_engine_list = list(filter(lambda item: item['type'] == 'mysql', engine_list))
    # 目前一种类型的数据库连接只支持一个，当前类型的数据库连接已存在时，直接抛出异常
    # 后续同一种类型的数据库连接会支持多个
    if target_engine_list:
        raise Exception("当前类型{}的数据库连接已存在，添加失败".format(type))
    engine_list.append({'type': type, "engine": engine})


def __get_depend_value(dependency, record):
    """
    寻找对应依赖的值
    :param dependency:
    :param record:
    :return:
    """
    tmp_list = []
    for tmp in dependency:
        id = tmp["id"]
        depend = tmp["depend"]
        tmp_record_list = list(filter(lambda item: item['id'] == id, record))
        if not tmp_record_list or len(tmp_record_list) > 1:
            raise Exception("在历史执行记录中查找对应的依赖值失败，依赖值id:{}".format(id))
        row = tmp_record_list[0]['row']
        for d in depend:
            tmp_list.append(row[d])
    return tmp_list


def __make_sql(sql, data, tmp_record):
    """
    生成断言业务数据需要的sql
    :param sql: 原始sql
    :param data: 当前数据校验的数据
    :param tmp_record：之前执行记录的结果
    :return:
    """
    if 'dependency' not in data.keys() or not data['dependency']:
        # 不满足处理sql的条件
        log.info("不满足处理sql的条件!")
        return sql
    dependency = data['dependency']
    tmp_list = __get_depend_value(dependency, tmp_record)
    return sql.format(*tmp_list)


def assert_biz_data(data):
    """
    断言持久化的业务数据
    :param data: 符合断言要求的数据格式内容
    :return:
    """
    try:
        tmp_record = []
        for tmp_data in data:
            type = tmp_data['type']
            sql = tmp_data['sql']
            if type == 'mysql':
                # 处理mysql数据的断言
                log.info("断言mysql业务数据")
                # 处理mysql
                sql = __make_sql(sql, tmp_data)
                # 执行mysql
                # TODO:执行sql语句，根据查询结果，进行业务数据判断
                results_rows = __get_engine("mysql").execute(sql)
                return True
            else:
                raise Exception("未知类型{},断言业务数据失败".format(type))
    except Exception as e:
        log.error(e)
        return False


if __name__ == '__main__':
    x = {}
    print(x['dependency'])
