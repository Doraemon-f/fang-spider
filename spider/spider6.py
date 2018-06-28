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

DOMAIN = 'http://esf.gz.fang.com'
__USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'


def __trans_code(response):
    return __unzip(response.read())


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


def trim(string):
    return string.replace(' ', '').replace('\n', '').replace('\r', '')


page_list = open('../detail/detail6.txt', 'r')
result = open('result6.csv', 'a+')
for page in page_list.readlines():
    try:
        url = (DOMAIN + page).replace('\n', '')
        html = fetch(url)
        print 'fetching page %s' % url
        soup = BeautifulSoup(html, 'html.parser')

        # 行政区
        district = trim(soup.find(id='agantesfxq_C03_07').string)

        # 商圈
        domain = trim(soup.find(id='agantesfxq_C03_08').string)

        # 小区
        garden = trim(soup.find(id='agantesfxq_C03_05').string)

        # 户型 建筑面积 单价 朝向 楼层 装修
        tags = soup.find_all(class_='tt')
        house_type = trim(tags[0].string)
        area = trim(tags[1].string)
        single_price = trim(tags[2].string)
        direction = trim(tags[3].string)
        floor = trim(tags[4].string)
        fitment = trim(tags[5].string)

        # 总价
        total_price = trim(soup.find(class_='price_esf').find('i').string)

        # 电梯
        elevator = trim(soup.find_all('span', text=u'有无电梯')[0].find_next_siblings()[0].string)

        # 挂牌时间
        date = trim(soup.find_all('span', text=u'挂牌时间')[0].find_next_siblings()[0].string)

        # 建筑年代
        period = trim(soup.find_all('span', text=u'建筑年代')[0].find_next_siblings()[0].string)

        # 评论
        comment = soup.find('ul', class_='fyms_modify').find(style='font-size:14px;').text

        line = [u'广州', district, domain, garden, url, house_type, area, total_price, '', direction, fitment, elevator,
                floor, period, comment, single_price, '', '', u'房天下', date, u'在售']

        result.write((u','.join(line) + '\n').encode('utf-8'))
    except BaseException as e:
        print e
result.close()
page_list.close()
