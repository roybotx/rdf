from constants import ZIPCODE_SEARCH_URL, UA, WAIT_TIME
from bs4 import BeautifulSoup
import requests
import logging
from proxy_tool import Proxy


class link_operation(object):
    def __init__(self, zipcode):
        self.request_url = ZIPCODE_SEARCH_URL + str(zipcode)
        self.proxy_tool = Proxy()
        self.proxy_tool.get_proxies()
        self.logger = logging.getLogger("link_operation")

    def __calc_total_page_num(self, url):
        try:
            pagination_str = self.html.find("div", {"class": "viewingPage"}).getText()
            pagination = int(pagination_str[len("Viewing page 1 of "): -len("(Download All)")])
            return [("%s/page-%d") % (url, i + 1)for i in range(1, pagination)]
        except Exception as e:
            self.logger.error("Unknow err in __calc_total_page_num().{}".format(str(e)))

    def __fetch_all_links_on_page(self):
        try:
            ls = [link.attrs.get("href") for link in self.html.findAll("a", {"class": "cover-all"})]
            return ls
        except Exception as e:
            self.logger.error("Unknow err in __fetch_all_links_on_page().{}".format(str(e)))

    def __make_call(self, url, retries):
        for attempt in range(retries):
            resp = None
            try:
                resp = requests.get(url, headers = {"user-agent": UA.random}, proxies = self.proxy_tool.get_available_proxy(WAIT_TIME))
            except Exception as e:
                self.logger.error("Unknow err in __make_call().{}\nTrying {} more time(s)...".format(str(e), 3 - attempt))
            else:
                self.html = BeautifulSoup(resp.text, "lxml")
                break

    def __is_roboted(self):
        return "looks like our usage analysis algorithms think that you\n    might be a robot" in self.html.text

    def fetch_all_pages(self):
        url = self.request_url
        self.__make_call(url, 3)
        if self.__is_roboted():
            self.__make_call(url, 3)
        self.pages = self.__calc_total_page_num(url)
        self.logger.info("{} pages in total to fetch.".format(len(self.pages) + 1))
        self.links = self.__fetch_all_links_on_page()
        self.logger.info("Got {} links on page {}".format(len(self.links), url))
        for page in self.pages:
            url = page   
            self.__make_call(url, 3)
            if self.__is_roboted():
                self.__make_call(url, 3)
            links_on_page = self.__fetch_all_links_on_page()
            self.links.extend(links_on_page) 
            self.logger.info("Got {} links on page {}".format(len(links_on_page), url))
        return self.links
