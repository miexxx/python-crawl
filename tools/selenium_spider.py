# -*- coding: utf-8 -*-
from selenium import webdriver
from scrapy.selector import Selector

#下拉效果 不加载图片 使用js
# Firefox_opt = webdriver.FirefoxOptions()
# prefs = {"profile.managed_default_content_sttings.images":2}
# Firefox_opt.add_experimental_option("prefs", prefs)
# firefox_options= Firefox_opt
browser = webdriver.Firefox()

browser.get("https://www.baidu.com/")
selector = Selector(text=browser.page_source)
browser.quit()
#phantomjs 无界面浏览器