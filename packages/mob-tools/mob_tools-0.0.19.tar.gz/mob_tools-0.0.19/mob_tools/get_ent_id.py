# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2022/4/15 16:24
# @Author: "John"
import re
from datetime import datetime
import pymongo
from hashlib import md5

from mob_tools.generate_mongo_ts import find_documents

ES_DATE_PATTERN = re.compile(r'^[12]\d{3}-\d{2}-\d{2}$')
SALT = 'dadh~mh,os?dha?chsdr#ua&dfa235@$315%casryhahf)*^*!'


def is_legal_esdate(es_date):
    if ES_DATE_PATTERN.findall(es_date):
        return True


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


BASE_INFO_PROJECTION = {'ent_id': 1, 'uncid': 1, 'regno': 1, 'esdate': 1}


def get_ent_id_with_regno(mob_mongo, regno, es_date):
    """
    :param regno:       regno
    :param es_date:     es_date
    :param mob_mongo:   mongoClient
    :return:
    """
    docs = find_documents(mob_mongo, 'scrapy_crawl_system', 'enterprise_base_info', {'regno': regno}, BASE_INFO_PROJECTION)
    # 该注册号查到的库存数据
    if docs:
        # 1、有的数据既有信用代码又有注册号，有的只有注册号没有信用代码。可以返回第二种情况的ent_id
        for doc in docs:
            if not doc.get('uncid'):
                ent_id = doc.get('ent_id')
                doc_es_date = doc.get('esdate')
                if es_date and es_date == doc_es_date:
                    return ent_id

    # 注册号查不到或者未正确匹配，则使用注册号生成一个 ent_id（18位长度，跟uncid保持一致）
    ent_id = '{0:m>18}'.format(regno).lower()
    return ent_id


def get_ent_id_with_uncid(mob_mongo, uncid):
    ret = mob_mongo.scrapy_crawl_system.enterprise_base_info.find_one({'uncid': uncid}, {'ent_id': 1})
    if ret:
        return ret.get('ent_id')
    else:
        return uncid.lower()


def md5hex(word):
    if not isinstance(type(word), str):
        word = str(word)
    return md5(word.encode('utf-8')).hexdigest()


def get_ent_id_by_ent_name(mob_mongo, ent_name, es_date):
    history_docs = find_documents(mob_mongo, 'scrapy_crawl_system', 'company_ent_id', {'company_name': ent_name}, {'ent_id': 1}, sort_value=pymongo.DESCENDING)

    if not history_docs:
        ent_id = 'mob_pid_' + md5hex(ent_name + SALT)[:10]
        return ent_id
    else:
        for hd in history_docs:
            tem_ent_id = hd.get('ent_id')
            doc = mob_mongo.scrapy_crawl_system.enterprise_base_info.find_one({'ent_id': tem_ent_id}, BASE_INFO_PROJECTION)
            if doc:
                # 没有成立日期，无法校验，查到就返回
                if not es_date:
                    return doc.get('ent_id')
                else:
                    if es_date == doc.get('esdate'):
                        return doc.get('ent_id')
            else:
                return tem_ent_id
        # 因为 esdate 无法通过校验导致获取不到 ent_id， 则生成新的 ent_id
        ent_id = 'mob_pid_' + md5hex(ent_name + es_date + SALT)[:10]
        return ent_id


def get_ent_id(mongo, ent_name, uncid='', regno='', previous_names='', esdate=''):
    """
    获取企业唯一标识 ent_id
    以 scrapy_crawl_system.company_ent_id 表为基础表。
    :param mongo:             MongoClient对象
    :param ent_name:          企业名称
    :param esdate:            成立日期
    :param regno:             注册号码
    :param uncid:             社会统一信用代码
    :param previous_names:    所有历史名称，用英文逗号隔开
    :return:                  ent_id（企业唯一标识）
    """

    if esdate and is_legal_esdate(esdate):
        es_date = esdate
    else:
        es_date = ""

    ent_name = ent_name.replace('(', '（').replace(')', '）')

    # 先用信用代码找(99.34%的企业有信用代码)
    if uncid:
        ent_id = get_ent_id_with_uncid(mongo, uncid)
        persist_company_ent_id(mongo, ent_id, ent_name, previous_names)
        return ent_id

    # 无信用代码，用注册号找
    if regno:
        ent_id = get_ent_id_with_regno(mongo, regno, es_date)
        persist_company_ent_id(mongo, ent_id, ent_name, previous_names)
        return ent_id

    # 没有信用代码, 用公司名称
    # (这边主要处理非工商来源的数据，如招聘等)
    if ent_name:
        ent_id = get_ent_id_by_ent_name(mongo, ent_name, es_date)
        persist_company_ent_id(mongo, ent_id, ent_name, previous_names)
        return ent_id


if __name__ == '__main__':
    pass
