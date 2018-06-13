from constants import ZIPCODE_SEARCH_URL, UA
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import re
import time
from constants import UA
from my_logger import logger


class link_operation(object):
    def __init__(self, zipcode):
        self.request_url = ZIPCODE_SEARCH_URL + str(zipcode) 

    def __calc_total_page_num(self, url):
        try:
            pagination_str = self.html.find("div", {"class": "viewingPage"}).getText()
            pagination = int(pagination_str[len("Viewing page 1 of "): -len("(Download All)")])
            self.links = self.__fetch_all_links_on_page()
            return [("%s/page-%d") % (url, i + 1)for i in range(1, pagination)]
        except Exception as e:
            logger.error("Unknow err in __fetch_all_links_on_page().{}".format(str(e)))

    def __fetch_all_links_on_page(self):
        try:
            return [link.attrs.get("href") for link in self.html.findAll("a", {"class": "cover-all"})]
        except Exception as e:
            logger.error("Unknow err in __fetch_all_links_on_page().{}".format(str(e)))

    def fetch_all_pages(self):
        try:
            resp = requests.get(self.request_url, headers = {"user-agent": UA.random})
            time.sleep(15)
            self.html = BeautifulSoup(resp.text, "lxml") 
            self.pages = self.__calc_total_page_num(self.request_url)
            for page in self.pages:
                self.html = BeautifulSoup(requests.get(page, headers = {"user-agent": UA.random}).text, "lxml")
                time.sleep(15)
                self.links.extend(self.__fetch_all_links_on_page())
            return self.links
        except Exception as e:
            logger.error("Unknow err in fetch_all_pages().{}".format(str(e)))