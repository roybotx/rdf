from constants import UA, WAIT_TIME
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
from proxy_tool import Proxy


class HomeOperation(object):
    def __init__(self, url):
        self.logger = logging.getLogger("HomeOperation")
        self.proxy_tool = Proxy()
        self.proxy_tool.get_proxies()
        self.__make_call(url)
        self.info = {"link": url}
        self.need_to_check = True
        self.logger.info("Just fetched the data from {}.".format(url))

    def __make_call(self, url):
        headers = {"user-agent": UA.random}
        for attempt in range(3):
            try:
                resp = requests.get(
                    url,
                    headers=headers,
                    proxies=self.proxy_tool.get_available_proxy(WAIT_TIME))
                self.html = BeautifulSoup(resp.text, "lxml")
                if self.__is_roboted():
                    raise Exception("Got roboted...")
            except Exception as e:
                self.logger.error("Failed to get resp from {}.{}".format(
                    url, str(e)))
                self.logger.error("Trying {} more time(3)...".format(3 - attempt))
            else:
                break

    def __is_roboted(self):
        return "looks like our usage analysis algorithms think that you\n    might be a robot" in self.html.text

    def fetch_data(self):
        # if "NOT FOR SALE" in str(self.html.contents):
        #     self.logger.warning("NOT FOR SALE")
        #     self.need_to_check = False
        #     return
        # elif "READY TO BUILD" in str(self.html.contents):
        #     self.logger.warning("NOT FOR SALE - READY TO BUILD")
        #     self.need_to_check = False
        #     return
        # self.fetch_main_content()
        self.__fetch_key_info()
        self.__fetch_basic_info()
        self.__postprocess_values()
        return self.info

    def __fetch_basic_info(self):
        try:
            section = self.html.find("div",
                                     {"class": re.compile("HomeInfo *")})
            if section is not None:
                top_stats = section.find("div",
                                         {"class": re.compile("top-stats")})
                bot_stats = section.find(
                    "div", {"class": re.compile("HomeBottomStats")})
                if top_stats is not None:
                    address = top_stats.find(
                        "span", {"itemprop": re.compile("streetAddress")})
                    city_state_zipcode = top_stats.find(
                        "span", {"class": re.compile("citystatezip")})
                    if address is not None:
                        self.info["address"] = address.getText().strip()
                    if city_state_zipcode is not None:
                        city = city_state_zipcode.find(
                            "span", {"itemprop": "addressLocality"})
                        state = city_state_zipcode.find(
                            "span", {"itemprop": "addressRegion"})
                        zipcode = city_state_zipcode.find(
                            "span", {"itemprop": "postalCode"})
                        if city is not None:
                            self.info["city"] = city.getText().strip().replace(
                                ",", "")
                        if state is not None:
                            self.info["state"] = state.getText().strip()
                        if state is not None:
                            self.info["zipcode"] = zipcode.getText().strip()
                    values = top_stats.findAll(True, {"class": "statsValue"})
                    labels = top_stats.findAll(True, {"class": "statsLabel"})
                    sqft_label = top_stats.find("span", {"class": "sqft-label"})
                    if sqft_label is not None:
                        self.info["sqft"] = values[-1].getText()
                        self.info["per_sqft"] = labels[-1].getText()
                    values.pop(-1)
                    labels.pop(-1)
                    if len(values) == len(labels):
                        for idx, value in enumerate(values):
                            label = labels[idx].getText()
                            label = self.__preprocess_field(label)
                            self.info[label] = value.getText()
                if bot_stats is not None:
                    values = bot_stats.findAll(True, {"class": "value"})
                    labels = bot_stats.findAll(True, {"class": "label"})
                    if len(values) == len(labels):
                        for idx, value in enumerate(values):
                            label = labels[idx].getText()
                            label = self.__preprocess_field(label)
                            self.info[label] = value.getText()
        except Exception as e:
            self.logger.error("fetch_basic_info - {}".format(str(e)))

    def __fetch_key_info(self):
        try:
            key_detail_list = self.html.find("div",
                                             {"class": "keyDetailsList"})
            if key_detail_list is not None:
                headers = key_detail_list.findAll(
                    "span", {"class": re.compile("header.*")})
                contents = key_detail_list.findAll(
                    "span", {"class": re.compile("content.*")})
                if len(headers) == len(contents):
                    for idx, header in enumerate(headers):
                        key = self.__preprocess_field(header.getText())
                        self.info[key] = contents[idx].getText()
        except Exception as e:
            self.logger.error("fetch_key_info() - {}".format(str(e)))

    def __fetch_main_content(self):
        amenities_container_div = self.html.find(
            "div", {"class": "amenities-container"})
        titles = amenities_container_div.findAll(
            "div", {"class": "super-group-title"})
        contents = amenities_container_div.findAll(
            "div", {"class": "super-group-content"})
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
                        main_content_details[self.__preprocess_field(
                            h4.getText())] = [detail.getText()]
                    else:
                        main_content_details[self.__preprocess_field(
                            h4.getText())].append(detail.getText())
            main_content[self.__preprocess_field(title)] = main_content_details
        # self.info.update(main_content)

    def __preprocess_field(self, prename):
        prename = prename.lstrip().rstrip()
        regex = re.compile('[%s]' % re.escape("#():."))
        prename = str.lower(prename).replace(" ", "_")
        res = regex.sub("", prename)
        if res == "baths":
            res = "bath"
        elif res == "sq_ft":
            res = "sqft"
        return res

    def __postprocess_values(self):
        key_of_number_dict = [
            "sqft", "per_sqft", "bath", "beds", "price", "lot_size", "built",
            "redfin_estimate", "last_sold_price", "hoa_dues",
            "listed_at_price", "on_redfin"
        ]
        key_of_date_dict = ["offer_review_date"]
        for key, value in self.info.items():
            if key in key_of_number_dict:
                self.info[key] = self.__process_number_value(value)
            elif key in key_of_date_dict:
                self.info[key] = self.__process_date_value(value)

    def __process_number_value(self, value):
        value = value.replace("—", "0")
        regex = re.compile("[\d(,.*)\d]+")
        res = regex.findall(value)
        return re.sub(",", "", res[0])

    def __process_date_value(self, value):
        return datetime.strptime(value,
                                 "%A, %B %d, %Y").strftime('%Y-%m-%d %H:%M:%S')

