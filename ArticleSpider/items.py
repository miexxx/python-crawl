# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy
import redis
from models.es_types import ArticleType
from models.ZhihuQuestion_es import ZhihuQuestionType
from models.ZhihuAnswer_es import ZhihuAnswerType
from models.Lagou_es import LagouType
from w3lib.html import remove_tags
from elasticsearch_dsl.connections import connections
jobbole_es = connections.create_connection(ArticleType._doc_type.using)
zhihu_question_es = connections.create_connection(ZhihuQuestionType._doc_type.using)
zhihu_answer_es = connections.create_connection(ZhihuAnswerType._doc_type.using)
lagou_job_es = connections.create_connection(LagouType._doc_type.using)

redis_cli = redis.StrictRedis()

def gen_suggests(index, info_tuple, es):
    #根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, params={'filter':["lowercase"]}, body={'text':text,'analyzer':"ik_max_word"})
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})
    return suggests
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    pass

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                insert into jobbole_article(create_date,fav_nums,comment_nums,front_image_url,url,url_object_id, praise_nums, tags, content, title, front_image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self["create_date"], self["fav_nums"], self["comment_nums"], self["front_image_url"], self["url"], self["url_object_id"], self["praise_nums"], self["tags"], self["content"], self["title"], self["front_image_path"])
        return insert_sql, params
    def save_to_es(self):
        article = ArticleType()
        article.title = self["title"]
        article.content = remove_tags(self["content"])
        article.front_image_url = self["front_image_url"]
        article.front_image_path = self["front_image_path"]
        article.praise_nums = self["praise_nums"]
        article.fav_nums = self["fav_nums"]
        article.comment_nums = self["comment_nums"]
        article.url = self["url"]
        article.url_object_id = self["url_object_id"]
        article.tags = self["tags"]
        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title,10),(article.tags,7)), jobbole_es)
        article.save()
        redis_cli.incr("jobbole_count")
        return

class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                insert into zhihu_question(zhihu_id, topics,url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self["zhihu_id"], self["topics"],self["url"], self["title"], self["content"], self["answer_num"], self["comments_num"], self["watch_user_num"], self["click_num"], self["crawl_time"])
        return insert_sql, params
    def save_to_es(self):
        question = ZhihuQuestionType()
        question.zhihu_id = self["zhihu_id"]
        question.topics = self["topics"]
        question.url = self["url"]
        question.title = self["title"]
        question.content = remove_tags(self["content"])
        question.answer_num = self["answer_num"]
        question.comments_num = self["comments_num"]
        question.watch_user_num = self["watch_user_num"]
        question.click_num = self["click_num"]
        question.crawl_time = self["crawl_time"]
        question.suggest = gen_suggests(ZhihuQuestionType._doc_type.index, ((question.title, 10), (question.topics, 7)),zhihu_question_es)
        question.save()
        redis_cli.incr("zhihu_count")
        return

class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num, create_time, update_time, crawl_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self["zhihu_id"], self["url"],self["question_id"], self["author_id"], self["content"], self["praise_num"], self["comments_num"], self["create_time"], self["update_time"], self["crawl_time"])
        return insert_sql, params
    def save_to_es(self):
        answer = ZhihuAnswerType()
        answer.zhihu_id = self["zhihu_id"]
        answer.url = self["url"]
        answer.question_id = self["question_id"]
        answer.author_id = self["author_id"]
        answer.content = remove_tags(self["content"])
        answer.praise_num = self["praise_num"]
        answer.comments_num = self["comments_num"]
        answer.create_time = self["create_time"]
        answer.update_time = self["update_time"]
        answer.crawl_time = self["crawl_time"]
        answer.save()

        return

class LagouJob(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field()
    work_years = scrapy.Field()
    degree_need = scrapy.Field()
    job_type = scrapy.Field()
    pulish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field()
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    tags = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                   insert into lagou_job(title, url , url_object_id , salary , job_city , work_years, degree_need , job_type, pulish_time , job_advantage, job_desc , job_addr , company_url , company_name , crawl_time , tags)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           """
        params = (
        self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"], self["work_years"],
        self["degree_need"], self["job_type"], self["pulish_time"], self["job_advantage"], self["job_desc"], self["job_addr"], self["company_url"],
        self["company_name"], self["crawl_time"], self["tags"])
        return insert_sql, params

    def save_to_es(self):
        job = LagouType()
        job.title = self["title"]
        job.url = self["url"]
        job.url_object_id = self["url_object_id"]
        job.salary = self["salary"]
        job.job_city = self["job_city"]
        job.work_years = self["work_years"]
        job.degree_need = self["degree_need"]
        job.job_type = self["job_type"]
        job.pulish_time = self["pulish_time"]
        job.job_advantage = self["job_advantage"]
        job.job_desc = remove_tags(self["job_desc"])
        job.job_addr = remove_tags(self["job_addr"])
        job.company_url = self["company_url"]
        job.company_name = self["company_name"]
        job.crawl_time = self["crawl_time"]
        job.tags = self["tags"]
        job.suggest = gen_suggests(LagouType._doc_type.index, ((job.title, 10), (job.tags, 8),(job.degree_need, 7), (job.job_type, 6), (job.company_name, 5)),
                                       lagou_job_es)
        job.save()
        redis_cli.incr("lagou_count")
        return

