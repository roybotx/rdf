import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import utils

"""Let's test -1 git a"""


def get_links_by_zipcode(zipcode):
    url = "https://www.redfin.com/zipcode/" + str(zipcode)
    print("Fetching links from zipcode %s..." % zipcode)


def get_links_by_zipcodes(zipcodes):
    for zipcode in zipcodes:
        links = get_links_by_zipcode(zipcode)
        utils.execute_db("scraping", "home_link", values = links, fields = ["link"])
        print("All done. %d links added to db." % (len(links)))


codes = utils.query_db("scraping", "zipcode", fields = ["zcode"], conditions = "where county = 'KingCounty' and code_type not in ('POBox', 'Unique')")
print("Going to fetch links through %d zipcode..." % len(codes))
get_links_by_zipcodes(codes)
