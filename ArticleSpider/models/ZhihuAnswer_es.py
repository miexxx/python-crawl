# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
class customAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}
ik_analyzer = customAnalyzer("ik_max_word", filter=["lowercase"])
class ZhihuAnswerType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    zhihu_id = Keyword()
    url = Keyword()
    question_id = Keyword()
    author_id = Keyword()
    content = Text(analyzer="ik_max_word")
    praise_num = Integer()
    comments_num = Integer()
    create_time = Date()
    update_time = Date()
    crawl_time = Date()
    class Meta:
        index = "zhihu"
        doc_type = "zhihu_answer"


if __name__ == "__main__":
    ZhihuAnswerType.init()