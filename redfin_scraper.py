import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd


class Unit(object):
    def __init__(self):
        self._url = "https://www.redfin.com/WA/Bothell/10818-NE-148th-Ln-98011/unit-P204/home/103957365"
        self.html = self.make_call()
        self.info = {}
        self.stats = None

    def make_call(self):
        user_agent = UserAgent()        
        headers = {"user-agent": str(user_agent.chrome)}
        resp = requests.get(self._url, headers = headers)
        return BeautifulSoup(resp.text, "lxml")        

    def fetch_data(self):
        self.fetch_main_content()
        self.fetch_key_info()
        self.fetch_basic_info()

    def fetch_basic_info(self):
        home_info = {}
        basic_info_div = self.html.find("div", {"class": "HomeInfo inline-block"})
        stats_and_built = basic_info_div.find("div", {"class": "HomeBottomStats"})
        stats = stats_and_built.find(text = "Status: ").parent.nextSibling.getText()
        home_info["stats"] = stats
        built = stats_and_built.find(text = "Built: ").parent.nextSibling.getText()
        home_info["built"] = built
        basic_info = basic_info_div.find("div", {"class": "top-stats"})
        addr = basic_info.next.getText()
        home_info["address"] = addr
        for div in basic_info.find("div", {"class": "HomeMainStats float-right"}):
            if div.name == "div":
                if "sqft" not in div.attrs.get("class"):
                    home_info[div.contents[0].getText()] = div.contents[1].getText()
                else:
                    total = div.getText()
                    home_info["sqft"] = total[: total.find("$")]
                    home_info["per_sqft"] = total[total.find("$"):]
        self.info["basic_info"] = home_info

    def fetch_key_info(self):
        key_info_elements = self.html.find("div", {"class": "keyDetailsList"}).findAll("div", {"class": "keyDetail font-size-base"})
        key_info = {}
        for key_info_el in key_info_elements:
            key_and_info = key_info_el.findChildren("span")
            key_info[key_and_info[0].getText()] = key_and_info[1].getText()
        self.info["key_info"] = key_info

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
                        main_content_details[h4.getText()] = [detail.getText()]
                    else:
                        main_content_details[h4.getText()].append(detail.getText())
            main_content[title] = main_content_details
        self.info["main_content"] = main_content

    def to_csv(self):
        file_name = self.info["basic_info"]["address"].replace(", ", "-").replace(" ", "-") + ".xlsx"
        wr = pd.ExcelWriter(file_name, engine = "xlsxwriter")
        for key, value in self.info.items():
            df = pd.DataFrame.from_dict(value, orient = "index")
            df.to_excel(wr, key)
        wr.save()


u = Unit()
u.fetch_data()
u.to_csv()