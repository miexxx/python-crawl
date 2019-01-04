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
class ZhihuQuestionType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    zhihu_id = Keyword()
    topics = Text(analyzer="ik_max_word")
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    answer_num = Integer()
    comments_num = Integer()
    watch_user_num = Integer()
    click_num = Integer()
    crawl_time = Date()
    class Meta:
        index = "zhihu"
        doc_type = "zhihu_question"

if __name__ == "__main__":
    ZhihuQuestionType.init()
