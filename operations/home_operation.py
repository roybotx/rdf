from constants import UA, WAIT_TIME
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
from proxy_tool import Proxy


class home_operation(object):
    def __init__(self, url):
        self.proxy_tool = Proxy()
        self.proxy_tool.get_proxies()
        self.html = self.make_call(url)
        self.info = {"link": url}
        self.need_to_check = True
        self.logger = logging.getLogger("home_operation")
        self.logger.info("Just fetched the data from {}.".format(url))
        # time.sleep(30)

    def make_call(self, url):
        headers = {"user-agent": UA.random}
        for attempt in range(3):
            try:
                resp = requests.get(url, headers = headers, proxies = self.proxy_tool.get_available_proxy(WAIT_TIME))
            except Exception as e:
                self.logger.error("Failed to get resp from {}\nTrying {} more time(3)...".format(url, 3 - attempt))
            else:
                return BeautifulSoup(resp.text, "lxml")

    def fetch_data(self):
        if "NOT FOR SALE" in str(self.html.contents): 
            self.logger.warning("NOT FOR SALE")
            self.need_to_check = False
            return
        elif "READY TO BUILD" in str(self.html.contents):
            self.logger.warning("NOT FOR SALE - READY TO BUILD")
            self.need_to_check = False
            return
        # self.fetch_main_content()
        self.__fetch_key_info()
        self.__fetch_basic_info()
        self.__postprocess_values()

    def __fetch_basic_info(self):
        try:
            section = self.html.find("div", {"class": "HomeInfo inline-block"})
            top_stats = section.contents[0]
            bot_stats = section.contents[1]
            address = top_stats.contents[0].getText()
            addr_info = address.split(", ")
            self.info["address"] = addr_info[0]
            self.info["state"] = addr_info[1].split(" ")[0]
            self.info["zipcode"] = addr_info[1].split(" ")[1]
            main_stats = top_stats.contents[1]
            sqft = int()
            per_sqft = int()
            for index, block in enumerate(main_stats):
                if index == len(main_stats) - 1:
                    break
                if len(block.contents) == 2:
                    value = block.contents[0].getText()
                    key = self.__preprocess_field(block.contents[1].getText())
                    self.info[key] = value
                elif len(block.contents) == 1:
                    sub_b = block.contents[0]
                    sqft = sub_b.contents[0].getText()
                    per_sqft = sub_b.contents[3].getText()
                    self.info["sqft"] = sqft
                    self.info["per_sqft"] = per_sqft

            stats_section = bot_stats.contents[1]
            more_info = bot_stats.contents[0].contents[0]
            stats = stats_section.find("span", {"class": "value"}).getText()
            self.info["stats"] = stats
            for i in range(1, len(more_info.contents)):
                key = more_info.contents[i].find("span", {"class": "label"}).getText()
                key = self.__preprocess_field(key)
                value = more_info.contents[i].find("span", {"class": "value"}).getText()
                self.info[key] = value
        except Exception as e:
            self.logger.error("Unknown error in fetch_basic_info. {}".format(str(e)))
            return

    def __fetch_key_info(self):
        try:
            key_info_elements = self.html.find("div", {"class": "keyDetailsList"}).findAll("div", {"class": re.compile(".*keyDetail.*")})
            for key_info_el in key_info_elements:
                key = self.__preprocess_field(key_info_el.contents[0].getText())
                value = key_info_el.contents[1].getText()
                self.info[key] = value
        except Exception as e:
            self.logger.error("Unknown error in fetch_key_info(). {}".format(str(e)))
            return

    def __fetch_main_content(self):
        amenities_container_div = self.html.find("div", {"class": "amenities-container"})
        titles = amenities_container_div.findAll("div", {"class": "super-group-title"})
        contents = amenities_container_div.findAll("div", {"class": "super-group-content"})
        main_content_elements = {}
        for i in range(len(titles)):
            main_content_elements[titles[i].text] = contents[i]
        main_content = {}
        for title, contents in main_content_elements.items():
            main_content_details = {}
            for el in contents:
                h4 = el.findAll("h4")[0]
                h4_details = h4.findNextSiblings("li")
                for detail in h4_details:
                    if h4.getText() not in main_content_details.keys():
                        main_content_details[self.__preprocess_field(h4.getText())] = [detail.getText()]
                    else:
                        main_content_details[self.__preprocess_field(h4.getText())].append(detail.getText())
            main_content[self.__preprocess_field(title)] = main_content_details
        # self.info.update(main_content)

    def __preprocess_field(self, prename):
        prename = prename.lstrip().rstrip()
        regex = re.compile('[%s]' % re.escape("#():"))
        prename = str.lower(prename).replace(" ", "_")
        res = regex.sub("", prename)
        if res == "baths":
            res = "bath"
        return res

    def __postprocess_values(self):
        key_of_number_dict = ["sqft", "per_sqft", "bath", "beds", "price", "lot_size", "built", "redfin_estimate", "last_sold_price", "hoa_dues", "listed_at_price", "on_redfin"]
        key_of_date_dict = ["offer_review_date"]
        for key, value in self.info.items():
            if key in key_of_number_dict:
                self.info[key] = self.__process_number_value(value)
            elif key in key_of_date_dict:
                self.info[key] = self.__process_date_value(value)

    def __process_number_value(self, value):
        regex = re.compile("[\d(,.*)\d]+")
        res = regex.findall(value)
        return re.sub(",", "", res[0])
    
    def __process_date_value(self, value):
        return datetime.strptime(value, "%A, %B %d, %Y").strftime('%Y-%m-%d %H:%M:%S')

# u = unit(constants.TEST_URL)
# u.fetch_data()
# hm = Home(u.info)
# hm_db = Home_db_control("housing")
# hm_db.add_unit(hm)