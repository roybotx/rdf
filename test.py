import MySQLdb
import constants
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
import utils


def get_zipcode_set():
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()
    cur.execute("select zcode from zipcodes where code_type = 'Standard' and county = 'KingCounty' and crawled != 1")
    zipcodes = [code[0] for code in cur.fetchall()]
    
    cur.close()
    db.close()
    return zipcodes    


def get_links():
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()
    cur.execute("select link from links order by link desc")
    links = [link[0] for link in cur.fetchall()]    
    cur.close()
    db.close()
    return links


def _update_links_crawled(l):
    logger = logging.getLogger("update_links_crawled")   
    try:
        db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
        cur = db.cursor()
        cur.execute("update links set crawled = 1 where link = '{}'".format(l))
        db.commit()
    except Exception as e:
        logger.err(e)
    finally:        
        cur.close()
        db.close()


def testmethod_test_get_homes(): 
    logger = logging.getLogger("testmethod_test_get_homes")    
    links = get_links()
    logger.info("{} links in total".format(len(links)))
    hm_db = HomeDBControl("housing")
    for link in links:
        try:
            u = HomeOperation(constants.BASE_URL + link)
            u.fetch_data()
            hm_db.add_unit(Home(u.info))   
            _update_links_crawled(link)
        except Exception as e:
            logger.error("error in {}.\n{}".format(link, str(e)))
    hm_db.close_engine()
    logger.info("testmethod_test_get_homes finished.")


def testmethod_test_get_links_for_open_homes():
    """ Get all open home links for all the zipcodes"""
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = "housing")
    cur = db.cursor()    
    logger = logging.getLogger("testmethod_test_get_links")
    try:
        codes = get_zipcode_set()
        lc = LinkDBControl(constants.HOME_TYPE.ON_SALE)
        for zipcode in codes:
            url = constants.ZIPCODE_SEARCH_URL + zipcode
            lo = LinkOperation(url)
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
        url = constants.ZIPCODE_SEARCH_URL + str(98011)
        lc = LinkDBControl(constants.HOME_TYPE.ON_SALE)
        lo = LinkOperation(url)
        links = lo.fetch_all_pages()
        if links is not None and len(links) > 0:
            lc.add_links(links)
        lc.close_engine()
    except Exception as e:
        logger.error("err in testmethod_test_get_links_98001().{}".format(str(e)))    
    logger.info("testmethod_test_get_links finished.")
    

def testmethod_test_proxies():
    px_tool = Proxy()
    px_tool.get_proxies()
    for i in range(0, 100):
        one = px_tool.get_available_proxy(constants.WAIT_TIME)
        html = requests.get("http://ip.chinaz.com/getip.aspx", headers = {"user-agent": constants.UA.random}, proxies = one, timeout = 10).text
        print(html)


def testmethod_get_single_home_page():
    home = HomeOperation("https://www.redfin.com/WA/Bothell/20056-94th-Dr-NE-98011/unit-8/home/59704159")
    home.fetch_data()
    print(home.info)


def testmethod_get_all_sold_home_links_in_three_months(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode) + constants.SOLD_IN_THREE_MONTHS_FILTER
    _fetch_links_by_url_save_to_db(url, constants.HOME_TYPE.SOLD)


def testmethod_get_all_sold_home_links(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode) + constants.SOLD_ALL_FILTER
    _fetch_links_by_url_save_to_db(url, constants.HOME_TYPE.SOLD)


def testmethod_get_pending_home_links(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode) + constants.PENDING_FILTER
    _fetch_links_by_url_save_to_db(url, constants.HOME_TYPE.PENDING)


def testmethod_get_open_home_links(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode)
    _fetch_links_by_url_save_to_db(url, constants.HOME_TYPE.ON_SALE)


def _fetch_links_by_url_save_to_db(url, home_type):   
    logger = logging.getLogger("_fetch_links_by_url_save_to_db")
    try: 
        lc = LinkDBControl(home_type)
        lo = LinkOperation(url)
        links = lo.fetch_all_pages()
        if links is not None and len(links) > 0:
            lc.add_links(links)
    except Exception as e:
        logger.error(e)
    finally:
        lc.close_engine


utils.config_logging()
# testmethod_get_open_home_links(98011)
# testmethod_get_all_sold_home_links(98011)
# testmethod_get_pending_home_links(98011)
testmethod_test_get_homes()

