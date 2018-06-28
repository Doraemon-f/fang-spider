#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" district_crawler """

__author__ = 'shiyu.feng'


import common.http_util as http
from bs4 import BeautifulSoup
import re

url = http.DOMAIN
soup = BeautifulSoup(http.fetch(url), 'html.parser')
children = soup.find('div', class_='qxName').find_all('a')
try:
    district = open('district.txt', 'wb')
    text = '\n'.join(str(child.get('href')) for child in children)
    district.write(text)
except BaseException as e:
    print e