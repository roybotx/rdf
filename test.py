import MySQLdb
import constants
import requests
from models.home import Home
from db_controls.db_controls import HomeDBControl
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
    hm_db = HomeDBControl()
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
    _fetch_links_by_url_save_to_db(url)


def testmethod_get_all_sold_home_links(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode) + constants.SOLD_ALL_FILTER
    _fetch_links_by_url_save_to_db(url)


def testmethod_get_pending_home_links(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode) + constants.PENDING_FILTER
    _fetch_links_by_url_save_to_db(url)


def testmethod_get_open_home_links(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode)
    _fetch_links_by_url_save_to_db(url)


def testmethod_get_all_homes_by_search_link(zipcode):
    url = constants.ZIPCODE_SEARCH_URL + str(zipcode)
    _fetch_links_by_url_save_to_db(url)


def _fetch_links_by_url_save_to_db(url):   
    logger = logging.getLogger("_fetch_links_by_url_save_to_db")
    try:
        lo = LinkOperation(url)
        links = lo.fetch_all_pages()
        if links is not None and len(links) > 0:
            for link in links:
                ho = HomeOperation(link)
                home_data = ho.fetch_data()
                hc = HomeDBControl()
                if len(home_data) == 1:
                    hc.add_unit(Home(home_data, False))
                else:
                    hc.add_unit(Home(home_data))
    except Exception as e:
        logger.error(e)
    finally:
        hc.close_engine


utils.config_logging()
# testmethod_get_open_home_links(98011)
# testmethod_get_all_sold_home_links(98011)
# testmethod_get_pending_home_links(98011)
# testmethod_test_get_homes()
# testmethod_get_all_homes_by_search_link(98011)

# ho = HomeOperation("https://www.redfin.com/WA/Bothell/11321-E-Riverside-Dr-98011/home/284605")
# ho.info["sqft"] = "dfasdf"
# hc = HomeDBControl()
# hc.add_unit(Home(ho.info))

