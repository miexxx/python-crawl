# -*- coding: utf-8 -*-
import requests
from scrapy.selector import Selector
import urlparse
import MySQLdb
conn = MySQLdb.connect('127.0.0.1', 'root', 'root', 'article_spider', charset="utf8", use_unicode=True)
cursor = conn.cursor()
def crawl_ips(url):
    #爬取西刺的高匿免费ip代理
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
    }
    re = requests.get(url=url, headers = headers)
    selector = Selector(text=re.text)
    all_trs = selector.css("#ip_list tr")
    ip_list = []
    for tr in all_trs[2:18]:
        speed = 0
        all_texts = tr.css("td::text").extract()
        ip = all_texts[0]
        port = all_texts[1]
        proxy_type = all_texts[4]
        ip_list.append((ip, port, proxy_type, speed))
    for ip_info in ip_list:
        cursor.execute(
            "insert proxy_ip(ip,port,speed,proxy_type) VALUES('{0}','{1}',{2},'{3}')".format(
                ip_info[0], ip_info[1], ip_info[3], ip_info[2]
            )
        )
        conn.commit()
    next_url = selector.css(".next_page::attr(href)").extract()[0]
    next_url = urlparse.urljoin("http://www.xicidaili.com/nn/", next_url)
    if next_url:
        crawl_ips(next_url)
    else:
        pass
crawl_ips("http://www.xicidaili.com/")
