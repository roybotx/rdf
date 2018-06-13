import MySQLdb
from constants import BASE_URL
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from models.home import Home
from db_controls.db_controls import (Home_db_control, Link_db_control)
import time
from my_logger import logger
from operations.home_operation import home_operation
from operations.link_operation import link_operation

zipcodes = []


def get_zipcode_set():
    global zipcodes
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()
    cur.execute("select zcode from zipcodes where code_type = 'Standard' and county = 'KingCounty'")
    zipcodes = [code[0] for code in cur.fetchall()]
    
    cur.close()
    db.close()
    return zipcodes


def fetch_links(zipcode):
    url = "https://www.redfin.com/zipcode/" + str(zipcode) + "/filter/include=sold-3mo"
    print("Fetching links from zipcode %s..." % zipcode)
    user_agent = UserAgent()        
    headers = {"user-agent": user_agent.random}
    resp = requests.get(url, headers = headers)
    html = BeautifulSoup(resp.text, "lxml")
    house_links = []
    house_links.extend([BASE_URL + link.attrs.get("href") for link in html.findAll("a", {"class": "cover-all"})])  
    print("sleeping for 5 seconds")
    time.sleep(5)

    pagination_str = html.find("div", {"class": "viewingPage"}).getText()
    pagination = int(pagination_str[len("Viewing page 1 of "): -len("(Download All)")])
    urls = [("%s/page-%d") % (url, i + 1)for i in range(1, pagination)]

    for u in urls:
        html = BeautifulSoup(requests.get(u, headers = headers).text, "lxml")
        print("sleeping for 5 seconds")
        time.sleep(5)
        house_links.extend([BASE_URL + link.attrs.get("href") for link in html.findAll("a", {"class": "cover-all"})])

    house_links_set = set(house_links)
    print("Done with %s. %d links added." % (url, len(house_links_set)))
    
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()
    cur.execute("insert into links(link) values ('" + "', '".join([link for link in house_links_set]) + "');")
    cur.commit()
    cur.close()
    db.close()


def get_links():
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()
    cur.execute("select link from links order by link desc")
    links = [link[0] for link in cur.fetchall()]    
    cur.close()
    db.close()
    return links

def testmethod_test_get_homes(): 
    links = get_links()
    logger.info("{} links in total".format(len(links)))
    hm_db = Home_db_control("housing")
    for link in links:
        try:
            u = home_operation(BASE_URL + link)
            u.fetch_data()
            if u.need_to_check:
                hm_db.add_unit(Home(u.info))   
        except Exception as e:
            logger.error("error in {}.\n{}".format(link, str(e)))
    hm_db.close_engine()

def testmethod_test_get_links():
    try:
        codes = get_zipcode_set()
        lc = Link_db_control("housing")
        for zipcode in codes:
            lo = link_operation(zipcode)
            links = lo.fetch_all_pages()
            if links is not None and len(links) > 0:
                lc.add_links(links)
        lc.close_engine()
    except Exception as e:
        logger.error("err in testmethod_test_get_links().{}".format(str(e)))
    

testmethod_test_get_links()
testmethod_test_get_homes() 

#   $4,868,000  5,774 Sq. Ft.   $843 / Sq. Ft.      5.5
# import re
# values = ["$4,868,000", "5,774 Sq. Ft.", "$843 / Sq. Ft.", "5.5"]
# regex = re.compile(r"[\d\(,.)*\d]+")
# for value in values:
#     res = regex.findall(value)[0]
#     res = re.sub(",", "", res)
#     print(res)



# u = unit("https://www.redfin.com/WA/Woodinville/15050-127th-Pl-NE-98072/home/143458227")
# u.fetch_data()
# print(u.info)