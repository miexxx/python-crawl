# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
import urlparse
import datetime
from scrapy.loader import ItemLoader
from ArticleSpider.utils.common import get_md5

from ArticleSpider.items import JobBoleArticleItem

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']
    custom_settings = {
        'ITEM_PIPELINES': {
            'ArticleSpider.pipelines.ElasticsearchPipeline': 2,
            'ArticleSpider.pipelines.ArticleImagePipeline': 1,
        }
    }
    def parse(self, response):
       #1.获取文章列表页中的文章url并且交给scrapy下载解析函数进行具体字段解析
       #2.获取下一页的url并交给scrapy进行下载
       post_nodes = response.css("#archive .floated-thumb .post-thumb a")
       for post_node in post_nodes:
           image_url = post_node.css("img::attr(src)").extract_first("")
           post_url = post_node.css("::attr(href)").extract_first("")
           yield Request(url=urlparse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)
       # 提取下一页
       next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
       if next_urls:
           yield Request(url=urlparse.urljoin(response.url, next_urls), callback=self.parse)

    def parse_detail(self, response):
        # Item实例化
        article_item = JobBoleArticleItem()
        #文章封面图
        front_image_url = response.meta.get("front_image_url","")

        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip()
        create_date=create_date[0:10]
        praise_nums = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        match_re = re.match(".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = match_re.group(1)
        else:
            fav_nums = 0
        comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = match_re.group(1)
        else:
            comment_nums = 0

        content = response.xpath("//div[@class='entry']").extract()[0]

        tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith(u"评论")]
        tags = ",".join(tag_list)

        article_item["title"] = title
        article_item["url"] = response.url
        article_item["url_object_id"] = get_md5(response.url)
        try:
            create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["comment_nums"] = comment_nums
        article_item["fav_nums"] = fav_nums
        article_item["tags"] = tags
        article_item["content"] = content

        #通过item_loader加载item
        # front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        # item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        # item_loader.add_css("title", ".entry-header h1::text")
        # item_loader.add_value("url", response.url)
        # item_loader.add_value("url_object_id", get_md5(response.url))
        # item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        # item_loader.add_value("front_image_url", [front_image_url])
        # item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        # item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        # item_loader.add_css("fav_nums", ".bookmark-btn::text")
        # item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        # item_loader.add_css("content", "div.entry")
        #
        # article_item = item_loader.load_item()
        yield article_item
