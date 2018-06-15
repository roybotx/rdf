import constants
import utils
import logging


class LinkOperation(object):
    def __init__(self, url):
        self.request_url = url
        self.logger = logging.getLogger("LinkOperation")

    def __calc_total_page_num(self, url):
        try:
            pagination_str = self.html.find("div", {"class": "viewingPage"}).getText()
            pagination = int(pagination_str[len("Viewing page 1 of "): -len("(Download All)")])
            return [("%s/page-%d") % (url, i + 1)for i in range(1, pagination)]
        except Exception as e:
            self.logger.error("Unknow err in __calc_total_page_num().{}".format(str(e)))

    def __fetch_all_links_on_page(self):
        try:
            ls = ["{}{}".format(constants.BASE_URL, link.attrs.get("href")) for link in self.html.findAll("a", {"class": "cover-all"})]
            return ls
        except Exception as e:
            self.logger.error("Unknow err in __fetch_all_links_on_page().{}".format(str(e)))

    def fetch_all_pages(self):
        url = self.request_url
        self.html = utils.make_call(url, 3)
        if utils.is_roboted(self.html):
            self.html = utils.make_call(url, 3)
        self.pages = self.__calc_total_page_num(url)
        self.logger.info("{} pages in total to fetch.".format(len(self.pages) + 1))
        self.links = self.__fetch_all_links_on_page()
        self.logger.info("Got {} links on page {}".format(len(self.links), url))
        for page in self.pages:
            url = page   
            self.html = utils.make_call(url, 3)
            if utils.is_roboted(self.html):
                self.html = utils.make_call(url, 3)
            links_on_page = self.__fetch_all_links_on_page()
            self.links.extend(links_on_page) 
            self.logger.info("Got {} links on page {}".format(len(links_on_page), url))
        return self.links
