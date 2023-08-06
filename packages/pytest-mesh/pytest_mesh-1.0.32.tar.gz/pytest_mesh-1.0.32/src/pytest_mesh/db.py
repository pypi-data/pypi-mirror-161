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
    return target_engine_list[0]['engine']


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
        log.info("当前类型{}的数据库连接已存在，无需再添加")
        return
        # raise Exception("当前类型{}的数据库连接已存在，添加失败".format(type))
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
        if id not in record.keys():
            raise Exception('断言异常，无法查找到id={}的依赖'.format(id))
        tmp_row = record.get(id)
        for d in depend:
            tmp_list.append(getattr(tmp_row, d))
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


def __assert(row, data):
    """
    校验数据
    :param row: 需要校验的数据库查询结果行数据，目前只支持一行
    :param data: 当前数据校验依赖数据
    :return:
    """
    if "assert_info" not in data.keys() or not data['assert_info']:
        log.info("assert_info 不存在，当前不断言数据")
        return True
    assert_info = data["assert_info"]
    # 一行查询数据的多个字段断言
    for info in assert_info:
        column = info['column']
        expect_value = info['expect_value']
        assert getattr(row, column) == expect_value


def assert_biz_data(data) -> bool:
    """
    断言持久化的业务数据
    :param data: 符合断言要求的数据格式内容
    数据格式内容样例
    [
      {
        "id": 1,
        "type": "mysql",
        "sql": "select * from crm_leads_level_match_info where bcz_uid = 1",
        "assert_info": []
      },
      {
        "id": 2,
        "type": "mysql",
        "action": "query",
        "sql": "select * from crm_leads_level where id = {0}",
        "assert_info": [
          {
            "column": "leads_level",
            "expect_value": "A"
          }
        ],
        "dependency": [
          {
            "id": 1,
            "depend": [
              "leads_level_id"
            ]
          }
        ]
      }
    ]
    :return:
    """
    is_ok = True
    try:
        tmp_record = {}
        for tmp_data in data:
            id = tmp_data['id']
            type = tmp_data['type']
            sql = tmp_data['sql']
            if type == 'mysql':
                # 处理mysql数据的断言
                log.info("断言mysql业务数据")
                # 处理mysql
                sql = __make_sql(sql, tmp_data, tmp_record)
                # 执行mysql
                # TODO:执行sql语句，根据查询结果，进行业务数据判断
                results_rows = __get_engine("mysql").execute(sql)
                # 目前只支持单行查询数据的依赖数据录入和校验
                if results_rows.rowcount != 1:
                    raise Exception("当前查询结果不等于1,目前只支持单行数据结果,请修改你的sql")
                row = next(results_rows)
                tmp_record[id] = row
                # 断言数据
                __assert(row, tmp_data)
            else:
                raise Exception("未知类型{},断言业务数据失败".format(type))
    except Exception as e:
        log.error(e)
        is_ok = False
    finally:
        return is_ok


if __name__ == '__main__':
    x = {}
    print(x['dependency'])
