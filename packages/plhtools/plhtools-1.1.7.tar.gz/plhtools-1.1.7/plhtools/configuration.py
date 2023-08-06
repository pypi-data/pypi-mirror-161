#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                                                                             
Author: penglinhan                                        
Email: 2453995079@qq.com                                
File: configuration.py
Date: 2021/2/9 下午3:47
'''

import configparser
import os
import sys

def get_cf_path(configname = None):
    curpath = sys.path[0]
    while curpath != '/':
        for file in os.listdir(curpath):
            if configname != None:
                if configname == file:
                    return curpath+'/'+file
            else:
                if '.ini' in file:
                    return curpath+'/'+file
        curpath =  os.path.dirname(curpath)
    return 'no find config file'

class configuration(object):
    def __init__(self,config_name=None):
        self._path = get_cf_path()
        self.cf = configparser.ConfigParser()
        self.cf.read(self._path,encoding='utf-8')
    def get_label(self,label = None,):
        item = self.cf.items(label)
        return item
    def get_label_value(self,label=None,key =None):
        value = self.cf.get(label, key)
        if value:
            return value
        else:
            return ''

if __name__ == '__main__':
    obj = configuration()
    item = obj.get_label('es')
    value = obj.get_label_value('es','host')
    print(item,value)
