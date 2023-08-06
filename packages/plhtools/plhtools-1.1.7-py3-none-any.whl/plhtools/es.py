#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                                                                             
Author: penglinhan                                        
Email: 2453995079@qq.com                                
File: es.py
Date: 2022/8/3 4:22 下午
'''
from elasticsearch_dsl import connections
from .configuration import  configuration
from elasticsearch.helpers import bulk


def get_es_config(label='', host='', user='', password=''):
    if label:
        con_obj = configuration()
        host = con_obj.get_label_value(label, 'host')
        user = con_obj.get_label_value(label, 'user')
        password = con_obj.get_label_value(label, 'pass')
    else:
        host = host
        user = user
        password = password
        label = 'default'
    if user and password:
        return connections.create_connection(alias=label, hosts=[host], http_auth=(user, password), timeout=300)
    return connections.create_connection(alias=label, hosts=[host], timeout=300)


class EsOp():
    def __init__(self, label='', host='', user='', password='', size=2000):
        self.conn = get_es_config(label=label, host=host, user=user, password=password)
        self.size = size
    def get_es_state(self):
        print(self.conn.cluster.state())
        print(self.conn.cluster.health())

    def get_es_info(self):
        return self.conn.info()

    def create_table(self,index_name):
        if self.conn.indices.exists(index=index_name) is not True:
            result = self.conn.indices.create(index=index_name)
            print(result)
            if 'acknowledged' in result.keys() and result['acknowledged']:
                return '创建index成功'
            else:
                return '创建失败'
        else:
            return 'index已存在'
    def delete_index(self,index_name):
        if self.conn.indices.exists(index=index_name) :
            result = self.conn.indices.delete(index_name, ignore=[400, 404])
            if 'acknowledged' in result.keys() and result['acknowledged']:
                return '成功删除index'
            else:
                return '删除失败'
        else:
            return '没有对应的index'

    def bulk_to_es(self,index_name,bulk_list,**kwargs):
        _length = len(bulk_list)
        if _length > 100:
            for i in range(0, _length, 100):
                bulk(self.conn, bulk_list[i: i + 100], index=index_name, **kwargs)
        else:
            bulk(self.conn, bulk_list, index=index_name, **kwargs)
    def index_search(self,index_name,body):
        result = self.conn.search(index=index_name, body=body)
        if result:
            items = result['hits']['hits']
            result_list= []
            for i in items:
                temp_dict = i['_source']
                temp_dict['_id'] = i['_id']
                result_list.append(temp_dict)
            return result_list
        else:
            return '未查到'
    def index_search_all(self,index_name,pn=1,size=10):
        body = {
            "query": {
                "match_all": {}
            },
            "from": (pn - 1) * size,
            "size": size,
        }
        return self.index_search(index_name,body)
    def index_search_absolute_match(self,index_name,quer_dict,pn=1,size=10):
        quer={}
        for i in quer_dict.keys():
            quer[i+'.keyword'] = quer_dict[i]
        body = {
            "query": {
                "term": quer
            },
            "from": (pn - 1) * size,
            "size": size,
        }
        return self.index_search(index_name,body)
    def index_search_fuzzy_match(self,index_name,quer_dict,pn=1,size=10):
        body = {
            "query": {
                "match":
                    quer_dict
            },
            "from": (pn - 1) * size,
            "size": size,
        }
        return self.index_search(index_name,body)


if __name__ == '__main__':
    es = EsOp(host='http://172.23.166.52:9200',user='esuser',password='ijnokm90')

    s = es.create_table('standard_platform')
    print(s)
    # s = es.delete_index('standard_platform')
    # print(s)
    # from  encryption_and_decryption import EncDec
    # rows = [{
    #     "_id": EncDec.uuid_encode('醉了1'),
    #     "question": '醉了1',
    #     "answer": '惆怅1'
    # }]
    # es.bulk_to_es('standard_platform',rows)
    #全量
    s = es.index_search_all('standard_platform')
    print(s)
    s= es.index_search_absolute_match('standard_platform',{'question': '醉了'})
    print(s)
    s = es.index_search_fuzzy_match('standard_platform',{'question': '醉了'})
    print(s)
    # s = es.index_search('standard_platform',body2)
    # print(s)