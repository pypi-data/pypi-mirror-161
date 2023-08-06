#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                                                                             
Author: penglinhan                                        
Email: 2453995079@qq.com                                
File: mysql.py
Date: 2022/8/1 4:58 下午
'''


import pymysql
import pandas as pd
from .configuration import  configuration
from sqlalchemy import create_engine



class mysql_class():
    def __init__(self, label=None, host=None, port=None, user=None, password=None, db=None):
        if label:
            config = configuration.configuration()
            self._host = config.get_label_value(label, 'host')
            self._port = int(config.get_label_value(label, 'port'))
            self._user = config.get_label_value(label, 'user')
            self._password = config.get_label_value(label, 'pass')
            self._db_name = db if db else config.get_label_value(label, 'db')
        else:
            self._host = host
            self._port = port
            self._user = user
            self._password = password
            self._db_name = db

    def __connect(self):
        try:
            self.con = pymysql.connect(host=self._host, port=self._port,user=self._user,password=self._password,database=self._db_name,charset="utf8")
            self.con1 = pymysql.connect(host=self._host, port=self._port, user=self._user, password=self._password,
                                       database=self._db_name, charset="GBK")
            db_info = {'host':self._host,'port':self._port,'user':self._user,'password':self._password,'database':self._db_name}
            self.engine = create_engine('mysql+pymysql://%(user)s:%(password)s@%(host)s/%(database)s?charset=utf8' % db_info,encoding='utf-8')
            self.cursor = self.con.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            raise e
    # 得到当前表的所有数据
    def get_all_df(self,table_name = None):
        try:
            self.__connect()
            df = pd.read_sql('select * from %s'%table_name,con=self.con)
            return df
        except Exception as e:
            raise e
        finally:
            self.__release()
    def get_sql_df(self,sql):
        try:
            self.__connect()
            df = pd.read_sql(sql,con=self.con)
            return df
        except Exception as e:
            raise e
        finally:
            self.__release()

    def get_sql_df_engine(self, sql):
        try:
            self.__connect()
            df = pd.read_sql_query(sql, con=self.con1,chunksize=1000)
            return df
        except Exception as e:
            raise e
        finally:
            self.__release()
    # 字典查询，参数：表名，字典，查询类型。查询类型支持type='and'/type='or',字典支持子列表或的查询
    def get_dict_df(self,table_name = None,search_dict = {},type = 'and'):
        try:
            self.__connect()
            sql  = 'select * from %s  where '%table_name
            count = 0
            for i in search_dict:
                if count >0 and type == 'and':
                    sql += ' and '
                if count>0 and type == 'or':
                    sql += ' or '
                if isinstance(search_dict[i],list):
                    count1= 0
                    sql += '('
                    for j in search_dict[i]:
                        if j == None:
                            if count1 > 0:
                                sql += ' or '
                            temp_str = '%s is null'%(i)
                            sql +=temp_str
                            count1 += 1
                        else:
                            if count1 > 0:
                                sql += ' or '
                            temp_str = '%s="%s"'%(i,j)
                            sql +=temp_str
                            count1 += 1
                    sql += ')'
                else:
                    if search_dict[i] ==None:
                        temp_str = '%s is null' % (i)
                        sql += temp_str
                    else:
                        temp_str = '%s="%s"'%(i,search_dict[i])
                        sql +=temp_str
                count +=1
            df = pd.read_sql(sql, con=self.con)
            return df
        except Exception as e:
            raise e
        finally:
            self.__release()
    # pandas写入新表中
    def write_df_all_newtable(self,df,table_name):
        try:
            self.__connect()
            df.to_sql(table_name,self.engine,if_exists='append',index=False,chunksize=1000)
        except Exception as e:
            raise e
        finally:
            self.__release()
    #pandas如果存在就更新，不存在则添加
    def write_df_update_append_table(self,df,table_name,primaryKey):
        try:
            self.__connect()
            primaryKey_list = list(df[primaryKey])
            exit_id = []
            new_id = []
            for i in primaryKey_list:
                id_sql = "select 1 from %s where %s = '%s' limit 1;"%(table_name,primaryKey,i)
                try:
                    one_df = pd.read_sql(id_sql,self.con)
                    if one_df.empty:
                        new_id.append(i)
                    else:
                        exit_id.append(i)
                except Exception as e:
                    new_id.append(i)
            if new_id:
                new_df = df[df[primaryKey].isin(new_id)]
                new_dict = new_df.to_dict('records')
                for i in new_dict:
                    for j in i.keys():
                        if isinstance(i[j], list):
                            i[j] = str(i[j])
                        if isinstance(i[j], dict):
                            i[j] = str(i[j])
                        if isinstance(i[j], str):
                            i[j] = (i[j].replace("'", "\""))
                new_df = pd.DataFrame(new_dict)
                new_df.to_sql(table_name,self.engine,if_exists='append',index=False,chunksize=1000)
            if exit_id:
                exit_df = df[df[primaryKey].isin(exit_id)]
                exit_dict_list = exit_df.to_dict('records')
                for i in exit_dict_list:
                    count2=0
                    set_sql = ''
                    for j in i.keys():
                        if j !=primaryKey:
                            if count2>0:
                                set_sql +=','
                            if isinstance(i[j], list):
                                i[j] = str(i[j])
                            if isinstance(i[j], dict):
                                i[j] = str(i[j])
                            if isinstance(i[j],str):
                                i[j] = (i[j].replace("'","\""))
                            if i[j]:
                                if i[j]!=i[j]:
                                    set_sql += "`%s` = null" % (j)
                                else:
                                    set_sql += "`%s` = '%s'" % (j, i[j])
                            else:
                                set_sql += "`%s` = null" % (j)
                            count2 +=1

                    exit_sql= "update %s set %s where %s = '%s';"%(table_name,set_sql,primaryKey,i[primaryKey])
                    # print(exit_sql)
                    # result= pd.read_sql_query(exit_sql,con=self.engine,chunksize=100)
                    self.cursor.execute(exit_sql)
                    self.con.commit()

        except Exception as e:
            raise e
        finally:
            self.__release()
    def implement_sql(self,sql):
        try:
            self.__connect()
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            raise e
        finally:
            self.__release()
    def __release(self):
        if self.cursor:
            self.cursor.close()
        if self.con:
            self.con.close()



if __name__ == '__main__':
    mysql_obj = mysql_class(label='kewei_mysql',db= 'kewei')
    # df = mysql_obj.get_all_df('news')
    df = mysql_obj.get_dict_df('news',{'title':'市政府召开常务会议 研究新版北京城市总体规划实施情况等事项 市长陈吉宁主持会议','id':[1,2,3]},'or')
    df['keywords'] = df['id'].apply(lambda x:x+1)
    print(df.columns)
    df['id'] = df['id'].apply(lambda x:x-3)
    mysql_obj.write_df_update_append_table(df,'news1','id')