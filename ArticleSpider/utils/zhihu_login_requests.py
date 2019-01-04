from selenium import webdriver
import requests
import json
import os
import time
session = requests.session()
try:
    import cookielib
except:
    import http.cookiejar as cookielib
from time import sleep
import re
# browser = webdriver.Firefox()
# url= 'https://www.zhihu.com/'
# s = requests.Session()
# s.headers.clear()
# browser.get(url)
# browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[2]/span').click()
# browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input').send_keys('13055447037')
# browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input').send_keys('AAAAAA123')
# browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').submit()
# cookies = browser.get_cookies()
# jsonCookies = json.dumps(cookies)
# with open('cookies.json', 'w') as f:
#     f.write(jsonCookies)
# print cookies
# time.sleep(5)
if os.path.exists("cookies.json"):
    print ("yes")
else:
    print ("no")
    browser = webdriver.Firefox()
    url= 'https://www.zhihu.com/'
    s = requests.Session()
    s.headers.clear()
    browser.get(url)
    browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[2]/span').click()
    browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input').send_keys('13055447037')
    browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input').send_keys('AAAAAA123')
    browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').submit()
    cookies = browser.get_cookies()
    jsonCookies = json.dumps(cookies)
    with open('cookies.json', 'w') as f:
        f.write(jsonCookies)
    print cookies
    time.sleep(5)
with open('cookies.json', 'r') as f:
    listCookies = json.loads(f.read())
print listCookies
