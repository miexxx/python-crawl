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
class LagouType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    salary = Keyword()
    job_city = Text(analyzer="ik_max_word")
    work_years = Keyword()
    degree_need = Keyword()
    job_type = Text(analyzer="ik_max_word")
    pulish_time = Keyword()
    job_advantage = Text(analyzer="ik_max_word")
    job_desc = Text(analyzer="ik_max_word")
    job_addr = Text(analyzer="ik_max_word")
    company_url = Keyword()
    company_name = Text(analyzer="ik_max_word")
    crawl_time = Date()
    tags = Text(analyzer="ik_max_word")
    class Meta:
        index = "lagou"
        doc_type = "job"


if __name__ == "__main__":
    LagouType.init()