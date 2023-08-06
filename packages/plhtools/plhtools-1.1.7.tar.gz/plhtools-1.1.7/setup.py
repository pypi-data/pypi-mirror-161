#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                                                                             
Author: penglinhan                                        
Email: 2453995079@qq.com                                
File: setup.py.py
Date: 2022/6/16 10:49 上午
'''

from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r") as f:
  long_description = f.read()

setup(name='plhtools',  # 包名
      version='1.1.7',  # 版本号
      description='彭麟汉的工具包',
      long_description=long_description,
      author='penglinhan',
      author_email='2453995079@qq.com',
      url='https://mp.weixin.qq.com/s/9FQ-Tun5FbpBepBAsdY62w',
      install_requires=[
          'pycryptodome',
          'eciespy',
          'configparser',
          'pymysql',
          'pandas',
          'sqlalchemy',
          'PyExecJS',
          'ltp',
          'elasticsearch_dsl',
      ],
      license='MIT License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],

      )
