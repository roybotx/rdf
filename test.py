import MySQLdb
from constants import BASE_URL, UA, WAIT_TIME
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from models.home import Home
from db_controls.db_controls import (HomeDBControl, LinkDBControl)
import time
from operations.home_operation import HomeOperation
from operations.link_operation import LinkOperation
from proxy_tool import Proxy
import logging


def get_zipcode_set():
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()
    cur.execute("select zcode from zipcodes where code_type = 'Standard' and county = 'KingCounty' and crawled != 1")
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
    logger = logging.getLogger("testmethod_test_get_homes")
    
    links = get_links()
    logger.info("{} links in total".format(len(links)))
    hm_db = HomeDBControl("housing")
    for link in links:
        try:
            u = HomeOperation(BASE_URL + link)
            u.fetch_data()
            if u.need_to_check:
                hm_db.add_unit(Home(u.info))   
        except Exception as e:
            logger.error("error in {}.\n{}".format(link, str(e)))
    hm_db.close_engine()
    logger.info("testmethod_test_get_homes finished.")


def testmethod_test_get_links():
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()    
    logger = logging.getLogger("testmethod_test_get_links")
    try:
        codes = get_zipcode_set()
        lc = LinkDBControl("housing")
        for zipcode in codes:
            lo = LinkOperation(zipcode)
            links = lo.fetch_all_pages()
            if links is not None and len(links) > 0:
                lc.add_links(links)
            cur.execute("update zipcodes set crawled = 1 where zcode = " + str(zipcode))
            db.commit()
        lc.close_engine()
    except Exception as e:
        logger.error("err in testmethod_test_get_links().{}".format(str(e)))
    finally:
        cur.close()
        db.close()
        logger.info("testmethod_test_get_links finished.")


def testmethod_test_get_links_98001():
    logger = logging.getLogger("testmethod_test_get_links_98001")
    try:
        lc = LinkDBControl("housing")
        lo = LinkOperation(98011)
        links = lo.fetch_all_pages()
        if links is not None and len(links) > 0:
            lc.add_links(links)
        lc.close_engine()
    except Exception as e:
        logger.error("err in testmethod_test_get_links_98001().{}".format(str(e)))    
    logger.info("testmethod_test_get_links finished.")
    

def testmethod_test():
    ho = HomeOperation("https://www.redfin.com/WA/Woodinville/15050-127th-Pl-NE-98072/home/143458227")
    ho.fetch_data()
    print(ho.info)


def testmethod_test_proxies():
    px_tool = Proxy()
    px_tool.get_proxies()
    for i in range(0, 100):
        one = px_tool.get_available_proxy(WAIT_TIME)
        html = requests.get("http://ip.chinaz.com/getip.aspx", headers = {"user-agent": UA.random}, proxies = one, timeout = 10).text
        print(html)


def testmethod_get_single_home_page():
    # no values for baths, beds, sqft
    home = HomeOperation("https://www.redfin.com/WA/Bothell/20056-94th-Dr-NE-98011/unit-8/home/59704159")
    home.fetch_data()
    print(home.info)


# utils.config_logging()
testmethod_get_single_home_page()
# testmethod_test_get_links()
# testmethod_test_proxies()
# testmethod_test_get_links_98001()
# testmethod_test_get_homes()


