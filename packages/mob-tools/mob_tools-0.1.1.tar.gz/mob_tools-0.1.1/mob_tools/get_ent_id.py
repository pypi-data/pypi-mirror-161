# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2022/4/15 16:24
# @Author: "John"
import re
import pymongo
from hashlib import md5

from mob_tools.mob_tools.generate_mongo_ts import find_documents

ES_DATE_PATTERN = re.compile(r'^[12]\d{3}-\d{2}-\d{2}$')
SALT = 'dadh~mh,os?dha?chsdr#ua&dfa235@$315%casryhahf)*^*!'

BASE_INFO_PROJECTION = {'ent_id': 1, 'uncid': 1, 'regno': 1, 'esdate': 1, 'status': 1}
RUNNING_STATUS = ['存续', '开业', '在业', '正常', '在营']


def is_legal_esdate(es_date):
    if ES_DATE_PATTERN.findall(es_date):
        return True


def get_ent_id_with_regno(mob_mongo, regno, es_date):
    """
    process crawler data not contains uncid (if contains uncid, can not arrive here)
    note :  all data in enterprise_base_info must contain uncid
    :param regno:       regno
    :param es_date:     es_date
    :param mob_mongo:   mongoClient
    :return:
    """
    docs = find_documents(mob_mongo, 'scrapy_crawl_system', 'enterprise_base_info', {'regno': regno}, BASE_INFO_PROJECTION)
    if docs:
        # query with regno may find data with uncid (current crawler data has no uncid, but enterprise data in db may contain this column)
        # regno is unique column as uncid
        for doc in docs:
            ent_id = doc.get('ent_id')
            doc_es_date = doc.get('esdate')
            if es_date and es_date == doc_es_date:
                return ent_id

    # 注册号查不到或者未正确匹配，则使用注册号生成一个 ent_id（18位长度，跟uncid保持一致）
    ent_id = '{0:m>18}'.format(regno).lower()
    return ent_id


def get_ent_id_with_uncid(mob_mongo, uncid):
    """
    note: all data in enterprise_base_info must contain uncid
    """
    ret = mob_mongo.scrapy_crawl_system.enterprise_base_info.find_one({'uncid': uncid}, {'ent_id': 1})
    if ret:
        return ret.get('ent_id')
    else:
        # maybe new data
        return uncid.lower()


def md5hex(word):
    if not isinstance(type(word), str):
        word = str(word)
    return md5(word.encode('utf-8')).hexdigest()


def get_ent_id_by_ent_name(mob_mongo, ent_name, es_date):
    """
    处理只有一个公司名称获取 ent_id 的情况
    这种情况一般是非工商数据。
    """
    history_docs = find_documents(mob_mongo, 'scrapy_crawl_system', 'company_ent_id', {'company_name': ent_name}, {'ent_id': 1}, sort_value=pymongo.DESCENDING)

    if not history_docs:
        ent_id = 'mob_pid_' + md5hex(ent_name + SALT)[:10]
        return ent_id
    else:
        tem_ent_id_status_li = []
        for hd in history_docs:
            tem_ent_id = hd.get('ent_id')
            docs = find_documents(mob_mongo, 'scrapy_crawl_system', 'enterprise_base_info', {'ent_id': tem_ent_id}, BASE_INFO_PROJECTION, sort_value=pymongo.DESCENDING)
            if docs:
                doc = docs[0]
                ent_status = doc.get('status')
                ent_esdate = doc.get('esdate')
                # 爬虫没有成立日期，无法校验，优先返回一条状态为正常的 ent_id
                if not es_date:
                    tem_ent_id_status_li.append((ent_status, tem_ent_id))
                # 有成立日期字段，且匹配数据库的成立日期，立即返回
                else:
                    if es_date == ent_esdate:
                        return tem_ent_id

        if tem_ent_id_status_li:
            for doc in tem_ent_id_status_li:
                status = doc[0]
                if status in RUNNING_STATUS:
                    return doc[1]

            return tem_ent_id_status_li[0][1]


def transfer_uncid_and_regno(uncid, regno):
    """
    判断 uncid 和 regno 是否合法
    note： uncid 长度 18位； regno 长度 13 或者 15 位
    """
    real_uncid = ''
    real_regno = ''

    if uncid:
        uncid = uncid.upper()
        if len(uncid) == 18:
            real_uncid = uncid
        elif len(uncid) == 15 or len(uncid) == 13:
            real_regno = uncid

    if regno:
        regno = regno.upper()
        if len(regno) == 18:
            if not real_uncid:
                real_uncid = regno
        elif len(regno) == 15 or len(regno) == 13:
            if not real_regno:
                real_regno = regno

    return real_uncid, real_regno


def transform_esdate(esdate):
    """
    return legal esdate or ""
    """
    if esdate and is_legal_esdate(esdate):
        return esdate
    return ""


def get_ent_id(mongo, ent_name, uncid='', regno='', esdate=''):
    """
    获取企业唯一标识 ent_id
    以 scrapy_crawl_system.company_ent_id 表为基础表。
    :param mongo:             MongoClient对象
    :param ent_name:          企业名称
    :param esdate:            成立日期，必须符合类似 2022-02-02 格式，否则会丢失不能使用
    :param regno:             注册号码
    :param uncid:             社会统一信用代码
    :return:                  ent_id（企业唯一标识）
    """

    esdate = transform_esdate(esdate)
    uncid, regno = transfer_uncid_and_regno(uncid, regno)
    ent_name = ent_name.replace('(', '（').replace(')', '）')

    if uncid:
        ent_id = get_ent_id_with_uncid(mongo, uncid)
        return ent_id

    # 程序走到这里，处理的一定不是工商数据，因为工商数据必须含有 uncid
    if regno:
        ent_id = get_ent_id_with_regno(mongo, regno, esdate)
        return ent_id

    if ent_name:
        ent_id = get_ent_id_by_ent_name(mongo, ent_name, esdate)
        return ent_id


if __name__ == '__main__':
    pass
