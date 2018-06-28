#coding=utf-8

#  lianjia.py
#  Marmot
#
#  Created by rock on 2018/6/22.
#  Copyright © 2018年 rock. All rights reserved.

import re,urllib2,random,time,math
import sys

#获取页面
def getPage(url,referUrl):
    try:
        delay=random.uniform(0.5,1.8)
        time.sleep(delay)
        headers = {'User-Agent':'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11','Cache-Control':'no-cache','Pragma':'no-cache','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Referer':referUrl}
        req = urllib2.Request(url=url,headers=headers)
        socket = urllib2.urlopen(req)
        return socket.read()
    except Exception,data:
        print data
return 'error'
    finally:
        try:
            if socket is not None:
                socket.close()
        except Exception,data:
            print data
    return 'error'

#格式化编码
def format_UTF8(html):
    html=html.replace('\x80','')
    html=html.decode("GBK",'ignore').encode("utf-8",'ignore')
    return html


#读取本地文件
def do_readFile(fileName):
    
    try:
        f=open(fileName,'r')
        return f.read()
    finally:
        if f:
            f.close()
    return ''

#总成交数解析
regex_filter_count = r'共找到[^>]+>\s*(\d+)'
def do_getttlCount(html):

    ttlCount = re.search(regex_filter_count,html,re.IGNORECASE)
    if ttlCount is None:
        return -1
    else:
        return ttlCount.group(1)

#筛选器解析
regex_filter_district = r'href="([^"]+)"\s*title="\S+?成交二手房[^>]+>([^<]+)</a>\s+'
regex_filter_area = r'href="(/chengjiao[^"]+)"\s*>([^<]+)</a>\s+'
regex_filter_years = r'<a\s*href="(/chengjiao[^"]+)[^<]+<span\s*class="checkbox[^>]+><[^<]+<span\s*class[^>]+>(\S*年[^<]+)'
regex_filter_rooms=r'<a\s*href="(/chengjiao[^"]+)[^<]+<span\s*class="checkbox[^>]+></span>[^>]+>([^<]+?室[^<]*)</span>'

#全局计数器
HOUSE_COUNT=0
CITY_HOUSE_COUNT=0
def do_crawl_chengjiao(city,cityUrl,rfUrl):
    
    #进入城市成交首页
    print '分流至城市页面',city,cityUrl,cityUrl
    html = getPage(cityUrl+'/chengjiao',rfUrl)
    #******************TEST******************
    #html = do_readFile('city.html')
    #******************TEST******************
    #分流至城区页面
    r_districts = re.compile(regex_filter_district, re.IGNORECASE)
    m_districts = r_districts.findall(html,re.IGNORECASE)
    for d in m_districts:
        districtUrl=cityUrl+d[0]
        districtNm=d[1]
        print '分流至城区页面',city,districtNm,districtUrl
        html = getPage(districtUrl,districtUrl)
        #******************TEST******************
        #html = do_readFile('district.html')
        #******************TEST******************
        #分流至商圈页面
        r_areas = re.compile(regex_filter_area, re.IGNORECASE)
        m_areas = r_areas.findall(html,re.IGNORECASE)
        for area in m_areas:
            areaUrl=cityUrl+area[0]
            areaNm=area[1]
            print '分流至商圈页面',city,districtNm,areaNm,areaUrl
            #if city=='北京' and districtNm in ('东城','西城','朝阳','海淀','丰台','石景山','通州','昌平','大兴','亦庄开发区','顺义','房山','门头沟','平谷','怀柔','密云','延庆'):
            #   continue
            html = getPage(areaUrl,districtUrl)
            #******************TEST******************
            #html = do_readFile('district.html')
            #******************TEST******************
            #分流至户型页面
            r_rooms = re.compile(regex_filter_rooms, re.IGNORECASE)
            m_rooms = r_rooms.findall(html,re.IGNORECASE)
            for room in m_rooms:
                roomUrl=cityUrl+room[0]
                roomNm=room[1]
                print '分流至户型页面',city,districtNm,areaNm,roomNm,roomUrl
                #******************TEST******************
                #html = do_readFile('areaYear.html')
                #******************TEST******************
                #取第一页数据
                html = getPage(roomUrl,areaUrl)
                do_parseList(city,districtNm,areaNm,room[1],html)
                ttlCount=do_getttlCount(html)
                print '共找到'+ttlCount+'套('+city+'-'+districtNm+'-'+areaNm+'-'+roomNm+')成交房源'
                
                if ttlCount<0:
                    continue
                else:
                    #计算分页取第二页之后数据
                    pageNum=int(math.ceil(int(ttlCount)/30.0))+1
                    if pageNum>101:
                        print '*********WARNING!!!'+city+'-'+districtNm+'-'+areaNm+roomNm
                        pageNum=100
                    for i in range(2,pageNum):
                        lstUrl=roomUrl.split('/')
                        pageUrl=areaUrl+'pg'+str(i)+lstUrl[len(lstUrl)-2]+'/'
                        print '分流至户型分页页面['+str(i)+']',city,districtNm,areaNm,roomNm,pageUrl
                        html = getPage(pageUrl,roomUrl)
                        do_parseList(city,districtNm,areaNm,room[1],html)


#list元素解析
regex_list=r'title"><a href="([^"]+)"[^>]+>([^<]+)<(.*?</div></div></li>)'
regexp_dealCycle=r'dealCycleTxt[^<]+<span>(.*?div>)'
regexp_houseInfo=r'houseIcon[^<]+</span>([^<]+)'
regexp_dealDate=r'dealDate[^>]+>([^<]+)'
regexp_totalPrice=r'totalPrice[^<]+<span[^>]+>([^<]+)'
regexp_positionInfo=r'positionIcon[^<]+</span>([^>]+)<'
regexp_source=r'source"[^>]*>([^<]+)'
regexp_unitPrice=r'unitPrice[^<]+<span[^>]+>([^<]+)'
regexp_houseTxt=r'dealHouseTxt[^<]+<span>(.*?div>)'
regexp_houseTxtList=r'>([^<]+)<'
#解析页面
def do_parseList(city,district,area,room,html):
    r_list = re.compile(regex_list, re.IGNORECASE)
    m_list = r_list.findall(html,re.IGNORECASE)
    for m in m_list:
        #0:url,1:title,2:dealCycle,3:houseInfo,4:dealDate,5:totalPrice,6:positionInfo,7:source,8:houseTxt
        houseInfo=['','','','','','','','','','',city,district,area,room]
        houseInfo[0]=m[0]
        houseInfo[1]=m[1].replace(' ','|')

        m_dealCycle=re.search(regexp_dealCycle,m[2],re.IGNORECASE)
        if m_dealCycle is not None:
            houseInfo[2]=re.sub('<[^>]+>','|',m_dealCycle.group(1))
        m_houseInfo=re.search(regexp_houseInfo,m[2],re.IGNORECASE)
        if m_houseInfo is not None:
            houseInfo[3]=m_houseInfo.group(1).replace('&nbsp;','').replace(' ','')
        m_dealDate=re.search(regexp_dealDate,m[2],re.IGNORECASE)
        if m_dealDate is not None:
            houseInfo[4]=m_dealDate.group(1)
        m_totalPrice=re.search(regexp_totalPrice,m[2],re.IGNORECASE)
        if m_totalPrice is not None:
            houseInfo[5]=m_totalPrice.group(1)
        m_positionInfo=re.search(regexp_positionInfo,m[2],re.IGNORECASE)
        if m_positionInfo is not None:
            houseInfo[6]=m_positionInfo.group(1)
        m_unitPrice=re.search(regexp_unitPrice,m[2],re.IGNORECASE)
        if m_unitPrice is not None:
            houseInfo[7]=m_unitPrice.group(1)
        m_houseTxt=re.search(regexp_houseTxt,m[2],re.IGNORECASE)
        if m_houseTxt is not None:
            houseInfo[8]=re.sub('<[^>]+>','|',m_houseTxt.group(1))
        m_source=re.search(regexp_source,m[2],re.IGNORECASE)
        if m_source is not None:
            houseInfo[9]=m_source.group(1)

        #计数器
        global HOUSE_COUNT,CITY_HOUSE_COUNT
        HOUSE_COUNT=HOUSE_COUNT+1
        print str(CITY_HOUSE_COUNT)+'-'+str(HOUSE_COUNT)+'-'+city+'###do_parseList###',','.join(houseInfo)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    cities={'https://bj.lianjia.com':'北京','http://you.lianjia.com/bt':'保亭','https://bd.fang.lianjia.com':'保定','https://cd.lianjia.com':'成都','https://cq.lianjia.com':'重庆','https://cs.lianjia.com':'长沙','http://you.lianjia.com/cm':'澄迈','https://chengde.fang.lianjia.com':'承德','https://cz.fang.lianjia.com':'滁州','https://dl.lianjia.com':'大连','https://dg.lianjia.com':'东莞','http://you.lianjia.com/dz':'儋州','http://you.lianjia.com/da':'定安','http://you.lianjia.com/dl1':'大理','https://dy.fang.lianjia.com':'德阳','https://fs.lianjia.com':'佛山','https://gz.lianjia.com':'广州','https://hz.lianjia.com':'杭州','https://hui.lianjia.com':'惠州','https://hk.lianjia.com':'海口','https://hf.lianjia.com':'合肥','https://hs.fang.lianjia.com':'衡水','https://hg.fang.lianjia.com':'黄冈','https://hd.fang.lianjia.com':'邯郸','https://jn.lianjia.com':'济南','https://jx.fang.lianjia.com':'嘉兴','https://jz.fang.lianjia.com':'晋中','https://km.fang.lianjia.com':'昆明','http://you.lianjia.com/ls':'陵水','https://lf.lianjia.com':'廊坊','http://you.lianjia.com/lg':'临高','http://you.lianjia.com/ld':'乐东','https://ly.fang.lianjia.com':'龙岩','https://leshan.fang.lianjia.com':'乐山','https://ms.fang.lianjia.com':'眉山','https://nj.lianjia.com':'南京','https://qd.lianjia.com':'青岛','http://you.lianjia.com/qh':'琼海','http://you.lianjia.com/qz':'琼中','https://quanzhou.fang.lianjia.com':'泉州','https://qy.fang.lianjia.com':'清远','https://qhd.fang.lianjia.com':'秦皇岛','https://sh.lianjia.com':'上海','https://sz.lianjia.com':'深圳','https://su.lianjia.com':'苏州','https://sjz.lianjia.com':'石家庄','https://sy.lianjia.com':'沈阳','http://you.lianjia.com/san':'三亚','https://sx.fang.lianjia.com':'绍兴','https://tj.lianjia.com':'天津','https://ty.fang.lianjia.com':'太原','https://wh.lianjia.com':'武汉','https://wx.lianjia.com':'无锡','http://you.lianjia.com/wc':'文昌','http://you.lianjia.com/wn':'万宁','http://you.lianjia.com/wzs':'五指山','https://weihai.fang.lianjia.com':'威海','https://xm.lianjia.com':'厦门','https://xa.lianjia.com':'西安','https://xz.fang.lianjia.com':'徐州','http://you.lianjia.com/xsbn':'西双版纳','https://xn.fang.lianjia.com':'咸宁','https://xt.fang.lianjia.com':'邢台','https://yt.lianjia.com':'烟台','https://zs.lianjia.com':'中山','https://zh.lianjia.com':'珠海','https://zz.lianjia.com':'郑州','https://zj.fang.lianjia.com':'镇江','https://zjk.fang.lianjia.com':'张家口','https://zhangzhou.fang.lianjia.com':'漳州'}
    
    for url in cities:
        if re.match('https://\w*\.lianjia\.com',url,re.IGNORECASE):
            global CITY_HOUSE_COUNT
            CITY_HOUSE_COUNT=CITY_HOUSE_COUNT+1
            do_crawl_chengjiao(cities[url],url,url)



