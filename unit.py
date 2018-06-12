import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import constants
import re
from models.home import Home
from db_controls.db_controls import Home_db_control
from datetime import datetime
import time


class unit(object):
    def __init__(self, url):
        self.html = self.make_call(url)
        self.info = {"link": url}
        self.need_to_check = True
        print("Just fetched the data from {}. sleeping for 5 seconds".format(url))
        time.sleep(5)

    def make_call(self, url):
        user_agent = UserAgent()
        headers = {"user-agent": str(user_agent.chrome)}
        resp = requests.get(url, headers = headers)
        return BeautifulSoup(resp.text, "lxml")

    def fetch_data(self):
        if "NOT FOR SALE" in str(self.html.contents):
            print("not for sale")
            self.need_to_check = False
            return
        self.fetch_main_content()
        self.fetch_key_info()
        self.fetch_basic_info()

    def fetch_basic_info(self):
        home_info = {}
        basic_info_div = self.html.find("div", {"class": "HomeInfo inline-block"})
        stats_and_built = basic_info_div.find("div", {"class": "HomeBottomStats"})
        stats = stats_and_built.find(text = "Status: ").parent.nextSibling.getText()
        home_info["stats"] = stats
        if stats != "Sold":
            built = stats_and_built.find(text = "On Redfin: ").parent.nextSibling.getText()
        else:
            built = stats_and_built.find(text = "Built: ").parent.nextSibling.getText()
        home_info["built"] = built
        basic_info = basic_info_div.find("div", {"class": "top-stats"})
        addr = basic_info.next.getText()
        home_info["address"] = addr
        state_and_zipcode = addr.split(", ")[1].split(" ")
        self.info["state"] = state_and_zipcode[0]
        self.info["zipcode"] = state_and_zipcode[1]
        regex = re.compile('.*HomeMainStats.*')
        for div in basic_info.find("div", {"class": regex}):
            if div.name == "div":
                if "sqft" not in div.attrs.get("class"):
                    key = div.contents[1].getText()
                    value = div.contents[0].getText()
                    if key in ["Redfin Estimate", "Last Sold Price", "Beds", "Bath"]:
                        if key in ["Redfin Estimate", "Last Sold Price"]:
                            value = value.replace(",", "").replace("$", "")
                        home_info[unit.preprocess_field(key)] = value
                    else:
                        home_info[unit.preprocess_field(value)] = key
                else:
                    total = re.findall(r"\d+", div.getText())
                    home_info["sqft"] = total[0]
                    home_info["per_sqft"] = total[1]
        self.info.update(home_info)

    def fetch_key_info(self):
        key_info_elements = self.html.find("div", {"class": "keyDetailsList"}).findAll("div", {"class": "keyDetail font-size-base"})
        key_info = {}
        for key_info_el in key_info_elements:
            key_and_info = key_info_el.findChildren("span")
            key = unit.preprocess_field(key_and_info[0].getText())
            value = key_and_info[1].getText()
            if key == "hoa_dues":
                key_info[key] = re.findall(r"\d+", value)
            elif key == "offer_review_date":
                key_info[key] = datetime.strptime(value, "%A, %B %d, %Y").strftime('%Y-%m-%d %H:%M:%S')
            else:
                key_info[key] = value
        self.info.update(key_info)

    def fetch_main_content(self):
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
                        main_content_details[unit.preprocess_field(h4.getText())] = [detail.getText()]
                    else:
                        main_content_details[unit.preprocess_field(h4.getText())].append(detail.getText())
            main_content[unit.preprocess_field(title)] = main_content_details
        # self.info.update(main_content)

    @staticmethod
    def preprocess_field(prename):
        prename = str.lower(prename).replace(" ", "_")
        regex = re.compile('[%s]' % re.escape("#()"))
        res = regex.sub("", prename)
        return res


# u = unit(constants.TEST_URL)
# u.fetch_data()
# hm = Home(u.info)
# hm_db = Home_db_control("housing")
# hm_db.add_unit(hm)