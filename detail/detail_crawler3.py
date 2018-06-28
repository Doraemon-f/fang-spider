#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" spider """
import thread
import threading

__author__ = 'shiyu.feng'

from bs4 import BeautifulSoup
import re

import urllib2
import urllib
import gzip
import StringIO

DOMAIN = 'http://esf.gz.fang.com/'
__USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'


def __trans_code(response):
    return __unzip(response.read()).decode('gbk').encode('utf-8')


def __unzip(data):
    data = StringIO.StringIO(data)
    gz = gzip.GzipFile(fileobj=data)
    data = gz.read()
    gz.close()
    return data


def fetch(url):
    request = urllib2.Request(url)
    request.add_header('User-Agent', __USER_AGENT)
    request.add_header('Accept-Encoding', 'gzip, deflate')
    return __trans_code(urllib2.urlopen(request))


page = open('../page/page3.txt', 'r')
detail = open('detail3.txt', 'a+')
for url in page.readlines():
    html = fetch(url)
    print 'fetching page %s' % url
    soup = BeautifulSoup(html, 'html.parser')
    dd = soup.find_all('dd', class_='info')
    text = ''
    for d in dd:
        try:
            text += d.find('p', class_='title').find('a').get('href') + '\n'
        except BaseException as e:
            print e
    detail.write(text)
detail.close()
page.close()
