# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LagouJob
from ArticleSpider.utils.common import get_md5
class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 1,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'user_trace_token=20171015132411-12af3b52-3a51-466f-bfae-a98fc96b4f90; LGUID=20171015132412-13eaf40f-b169-11e7-960b-525400f775ce; SEARCH_ID=070e82cdbbc04cc8b97710c2c0159ce1; ab_test_random_num=0; X_HTTP_TOKEN=d1cf855aacf760c3965ee017e0d3eb96; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DsXIrWUxpNGLE2g_bKzlUCXPTRJMHxfCs6L20RqgCpUq%26wd%3D%26eqid%3Dee53adaf00026e940000000559e354cc; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_hotjob; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAAFCAAEG50060B788C4EED616EB9D1BF30380575; _gat=1; _ga=GA1.2.471681568.1508045060; LGSID=20171015203008-94e1afa5-b1a4-11e7-9788-525400f775ce; LGRID=20171015204552-c792b887-b1a6-11e7-9788-525400f775ce',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        },
        'ITEM_PIPELINES': {
            'ArticleSpider.pipelines.ElasticsearchPipeline': 2,
        }
    }

    rules = (
        Rule(LinkExtractor(allow=("gongsi/.*",)), follow=True),
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("jobs/list.*",)), follow=True),
        Rule(LinkExtractor(allow=("xiaoyuan.lagou.com.*",)), follow=True),
        Rule(LinkExtractor(allow=r'.*jobs/\d+.html'), callback='parse_job', follow=True),
    )
    def parse_start_url(self, response):
        return []

    def process_results(self, response, results):
        return results

    def parse_job(self, response):
        #解析拉钩网的职位
        title = response.css('.job-name::attr(title)').extract()
        url = response.url
        url_object_id = get_md5(response.url)
        salary = response.css('.job_request .salary::text').extract()
        job_city = response.css('.job_request > p:nth-child(1) > span:nth-child(2)::text').extract()
        work_years = response.css('.job_request > p:nth-child(1) > span:nth-child(3)::text').extract()
        degree_need =response.css('.job_request > p:nth-child(1) > span:nth-child(4)::text').extract()
        job_type = response.css('.job_request > p:nth-child(1) > span:nth-child(5)::text').extract()
        pulish_time = response.css('.publish_time::text').extract()
        tags = response.css('.position-label li::text').extract()
        tags = ",".join(tags)
        job_advantage = response.css('.job-advantage p::text').extract()
        job_desc = response.css('.job_bt div').extract()[0]
        job_addr = response.css('.work_addr').extract()[0]
        company_url = response.css('#job_company dt a::attr(href)').extract()
        company_name = response.css('#job_company dt a img::attr(alt)').extract()
        crawl_time = datetime.datetime.now().date()

        LagouJobItem =LagouJob()
        LagouJobItem["title"] = title
        LagouJobItem["url"] = url
        LagouJobItem["url_object_id"] = url_object_id
        LagouJobItem["salary"] = salary
        LagouJobItem["job_city"] = job_city
        LagouJobItem["work_years"] = work_years
        LagouJobItem["degree_need"] = degree_need
        LagouJobItem["job_type"] = job_type
        LagouJobItem["pulish_time"] = pulish_time
        LagouJobItem["job_advantage"] = job_advantage
        LagouJobItem["job_desc"] = job_desc
        LagouJobItem["job_addr"] = job_addr
        LagouJobItem["company_url"] = company_url
        LagouJobItem["company_name"] = company_name
        LagouJobItem["crawl_time"] = crawl_time
        LagouJobItem["tags"] = tags
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        yield  LagouJobItem
