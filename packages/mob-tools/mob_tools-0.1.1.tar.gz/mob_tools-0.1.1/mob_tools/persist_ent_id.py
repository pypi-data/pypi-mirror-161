# -*- coding: utf-8 -*-
"""
@Auth： John_Zy
@Time： 2022/8/2 下午4:47
@File： persist_ent_id.py
"""
from datetime import datetime

import pymongo


def persist_company_ent_id(mob_mongo, ent_id, ent_name, previous_names):
    """
    :param ent_id:          ent_id
    :param mob_mongo:       mongoClient
    :param ent_name:        ent_name
    :param previous_names:  所有历史名称，用英文逗号隔开
    :return:
    """
    all_names = [ent_name]
    if previous_names:
        previous_name_list = previous_names.split(',')
        all_names.extend(previous_name_list)

    doc_list = [{'ent_id': ent_id, 'company_name': item, 'update_time': datetime.now()} for item in all_names]
    try:
        mob_mongo.scrapy_crawl_system.company_ent_id.insert_many(doc_list, ordered=False)
    except pymongo.errors.BulkWriteError:
        # 主键冲突，无法写入，使用ordered=False保证其他数据可以入库即可
        pass
