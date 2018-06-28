#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" domain_crawler """

__author__ = 'shiyu.feng'

import common.http_util as http
from bs4 import BeautifulSoup
import re

district = open('../district/district.txt', 'r')
for url_part in district.readlines():
    url = http.DOMAIN + url_part
    print 'fetching %s' % url
    html = http.fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    children = soup.find(id='shangQuancontain').find_all('a')
    try:
        domain = open('domain.txt', 'a+')
        text = ''
        for child in children:
            text += child.get('href') + '\n'
        domain.write(text)
    except BaseException as e:
        print e
