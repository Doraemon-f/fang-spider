#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" spider """

__author__ = 'shiyu.feng'

import common.http_util as http
from bs4 import BeautifulSoup
import re


def __find_page(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    return int(soup.find(class_='fanye').find('span').string.replace(u'共', u'').replace(u'页', u''))


domain = open('../domain/domain.txt', 'r')
pages = open('page.txt', 'a+')
for url_part in domain.readlines():
    url = http.DOMAIN + url_part
    print 'fetching %s' % url
    html = http.fetch(url)
    max_page_number = __find_page(html)
    text = ''
    for index in range(1, max_page_number + 1):
        page_url = url.replace('\n', '') + 'i3' + str(index) + '/'
        text += page_url + '\n'
    pages.write(text)
pages.close()

