import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import utils

"""Let's test -1 """


def get_links_by_zipcode(zipcode):
    url = "https://www.redfin.com/zipcode/" + str(zipcode)
    print("Fetching links from zipcode %s..." % zipcode)
    user_agent = UserAgent()        
    headers = {"user-agent": user_agent.random}
    resp = requests.get(url, headers = headers)
    html = BeautifulSoup(resp.text, "lxml") 
    house_links = []
    house_links.extend([link.attrs.get("href") for link in html.findAll("a", {"class": "cover-all"})])  
    utils.SLEEP_FOR_15_SEC()

    pagination_str = html.find("div", {"class": "viewingPage"}).getText()
    pagination = int(pagination_str[len("Viewing page 1 of "): -len("(Download All)")])
    urls = [("%s/page-%d") % (url, i + 1)for i in range(1, pagination)]

    for u in urls:
        html = BeautifulSoup(requests.get(u, headers = headers).text, "lxml")
        utils.SLEEP_FOR_15_SEC()
        house_links.extend([link.attrs.get("href") for link in html.findAll("a", {"class": "cover-all"})])

    house_links_set = set(house_links)
    print("Done with %s. %d links added." % (url, len(house_links_set)))
    return house_links_set


def get_links_by_zipcodes(zipcodes):
    for zipcode in zipcodes:
        links = get_links_by_zipcode(zipcode)
        utils.execute_db("scraping", "home_link", values = links, fields = ["link"])
        print("All done. %d links added to db." % (len(links)))


codes = utils.query_db("scraping", "zipcode", fields = ["zcode"], conditions = "where county = 'KingCounty' and code_type not in ('POBox', 'Unique')")
print("Going to fetch links through %d zipcode..." % len(codes))
get_links_by_zipcodes(codes)
