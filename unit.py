import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import constants
import re


class unit(object):
    def __init__(self, url):
        self.html = self.make_call(url)
        self.info = {}

    def make_call(self, url):
        user_agent = UserAgent()        
        headers = {"user-agent": str(user_agent.chrome)}
        resp = requests.get(url, headers = headers)
        return BeautifulSoup(resp.text, "lxml")        

    def fetch_data(self):
        self.fetch_main_content()
        self.fetch_key_info()
        self.fetch_basic_info()
        self.to_properties()

    def to_properties(self):
        # for dic in self.info.values():
        for key, value in self.info["basic_info"].items():
            setattr(self, key, value)
        for key, value in self.info["key_info"].items():
            setattr(self, key, value)

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
                    if div.contents[1].getText() in ["Redfin Estimate", "Last Sold Price", "Beds", "Bath"]:
                        home_info[unit.preprocess_field(div.contents[1].getText())] = div.contents[0].getText()
                    else:
                        home_info[unit.preprocess_field(div.contents[0].getText())] = div.contents[1].getText()
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
            key_info[unit.preprocess_field(key_and_info[0].getText())] = key_and_info[1].getText()
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
                        main_content_details[unit.preprocess_field(h4.getText())] = [detail.getText()]
                    else:
                        main_content_details[unit.preprocess_field(h4.getText())].append(detail.getText())
            main_content[unit.preprocess_field(title)] = main_content_details
        self.info["main_content"] = main_content

    @staticmethod
    def preprocess_field(prename):
        prename = str.lower(prename).replace(" ", "_")
        regex = re.compile('[%s]' % re.escape("#()"))
        res = regex.sub("", prename)
        return res

# region Properties getter and setter
    @property
    def stats(self):
        return self._stats
    
    @stats.setter
    def stats(self, stats):
        self._stats = stats

    @property
    def built(self):
        return self._built
    
    @built.setter
    def built(self, built):
        self._built = built

    @property
    def address(self):
        return self._address
    
    @address.setter
    def address(self, address):
        self._address = address
    
    @property
    def redfin_estimate(self):
        return self._redfin_estimate
    
    @redfin_estimate.setter
    def redfin_estimate(self, redfin_estimate):
        self._redfin_estimate = redfin_estimate
    
    @property
    def last_sold_price(self):
        return self._last_sold_price
    
    @last_sold_price.setter
    def last_sold_price(self, last_sold_price):
        self._last_sold_price = last_sold_price
    
    @property
    def beds(self):
        return self._beds
    
    @beds.setter
    def beds(self, beds):
        self._beds = beds
    
    @property
    def bath(self):
        return self._bath
    
    @bath.setter
    def bath(self, bath):
        self._bath = bath
    
    @property
    def sqft(self):
        return self._sqft
    
    @sqft.setter
    def sqft(self, sqft):
        self._sqft = sqft
    
    @property
    def per_sqft(self):
        return self._per_sqft
    
    @per_sqft.setter
    def per_sqft(self, per_sqft):
        self._per_sqft = per_sqft
    
    @property
    def hoa_dues(self):
        return self._hoa_dues
    
    @hoa_dues.setter
    def hoa_dues(self, hoa_dues):
        self._hoa_dues = hoa_dues
    
    @property
    def property_type(self):
        return self._property_type
    
    @property_type.setter
    def property_type(self, property_type):
        self._property_type = property_type
    
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, style):
        self._style = style
    
    @property
    def floor_number(self):
        return self._floor_number
    
    @floor_number.setter
    def floor_number(self, floor_number):
        self._floor_number = floor_number
    
    @property
    def stories(self):
        return self._stories
    
    @stories.setter
    def stories(self, stories):
        self._stories = stories
    
    @property
    def views(self):
        return self._views
    
    @views.setter
    def views(self, views):
        self._views = views
    
    @property
    def offer_review_date(self):
        return self._offer_review_date
    
    @offer_review_date.setter
    def offer_review_date(self, offer_review_date):
        self._offer_review_date = offer_review_date
    
    @property
    def community(self):
        return self._community
    
    @community.setter
    def community(self, community):
        self._community = community
    
    @property
    def county(self):
        return self._county
    
    @county.setter
    def county(self, county):
        self._county = county
    
    @property
    def mls(self):
        return self._mls
    
    @mls.setter
    def mls(self, mls):
        self._mls = mls    
# endregion


u = unit(constants.TEST_URL)
u.fetch_data()
