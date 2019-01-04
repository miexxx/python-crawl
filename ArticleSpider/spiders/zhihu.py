# -*- coding: utf-8 -*-
import scrapy
import requests
import os
import time
import json
import urlparse
import re
import datetime
from ArticleSpider.items import ZhihuQuestionItem
from ArticleSpider.items import ZhihuAnswerItem
try:
    import cookielib
except:
    import http.cookiejar as cookielib
from selenium import webdriver

from time import sleep

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    #第一页的Answer 请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?limit={1}&offset={2}&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp&data%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type=best_answerer%29%5D.topics&data%5B%2A%5D.mark_infos%5B%2A%5D.url=&sort_by=default"
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'ITEM_PIPELINES': {
            'ArticleSpider.pipelines.ElasticsearchPipeline': 2,
        }
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
    }
    username = '13055447037'
    password = 'AAAAAA123'
    def parse(self, response):
        #提取html页面的所有url并根据url进一步爬取
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [urlparse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                requst_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(requst_url, headers=self.headers, callback=self.parse_question, meta={"question_id":question_id})
            else:
                yield scrapy.Request(url, headers=self.headers)

    def parse_question(self, response):
        #处理question 页面的question item
        question_item = ZhihuQuestionItem()
        title = response.css(".QuestionHeader-title::text").extract()[0]
        content = response.css(".QuestionHeader-detail").extract()[0]
        url = response.url
        zhihu_id = response.meta.get("question_id","")
        answer_num = response.css(".List-headerText span::text").extract()[0]
        answer_num = re.sub(',', '', answer_num)
        comments_num = response.css(".QuestionHeader-Comment > button:nth-child(1)::text").extract()[0]
        comments_num = re.sub(',', '', comments_num)
        match_obj = re.match(".*(\d+).*", comments_num)
        if match_obj:
            comments_num = match_obj.group(1)
        else:
            comments_num = 0
        watch_user_num = response.css("div.NumberBoard-item > div:nth-child(1) > strong:nth-child(2)::text").extract()[0]
        if watch_user_num:
            watch_user_num = re.sub(',', '', watch_user_num)
        else:
            watch_user_num = 0
        click_num = response.css("div.NumberBoard-item > div:nth-child(1) > strong:nth-child(2)::text").extract()[0]
        click_num = re.sub(',', '', click_num)
        topics = response.css(".QuestionHeader-topics .Popover div::text").extract()
        topics = ",".join(topics)
        question_item["zhihu_id"] = zhihu_id
        question_item["topics"] = topics
        question_item["url"] = url
        question_item["title"] = title
        question_item["content"] = content
        question_item["answer_num"] = answer_num
        question_item["comments_num"] = comments_num
        question_item["watch_user_num"] = watch_user_num
        question_item["click_num"] = click_num
        question_item["crawl_time"] = datetime.datetime.now().date()
        yield scrapy.Request(self.start_answer_url.format(zhihu_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item
    def parse_answer(self, response):
        #处理anwser
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        totals_answer = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]
        #提取answer字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(answer["created_time"]))
            answer_item["crawl_time"] = datetime.datetime.now().date()
            answer_item["update_time"] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(answer["updated_time"]))

            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)


    def get_cookies(self):
        #selenium模拟登录存取cookie
        browser = webdriver.Firefox()
        url = 'https://www.zhihu.com/'
        s = requests.Session()
        s.headers.clear()
        browser.get(url)
        browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[2]/span').click()
        browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input').send_keys(self.username)
        browser.find_element_by_xpath(
            '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input').send_keys(self.password)
        time.sleep(5)
        browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').submit()
        time.sleep(2)
        time.sleep(5)
        cookies = browser.get_cookies()
        time.sleep(2)
        jsonCookies = json.dumps(cookies)
        with open('cookies.json', 'w') as f:
            f.write(jsonCookies)
        browser.quit()
        return cookies

    def start_requests(self):
        if os.path.exists("cookies.json"):
            with open('cookies.json', 'r') as f:
                listCookies = json.loads(f.read())
            self.cookies=listCookies
        else:
            self.cookies = self.get_cookies()
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, dont_filter=True)



