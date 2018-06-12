import MySQLdb
from constants import BASE_URL
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from unit import unit
from models.home import Home
from db_controls.db_controls import Home_db_control
import time

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


# codes = get_zipcode_set()


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
    

links = get_links()
units = []
hm_db = Home_db_control("housing")
for link in links:
    u = unit(BASE_URL + link)
    u.fetch_data()
    if u.need_to_check:
        if len(hm_db.select_units(link = u.info["link"])) > 0:
            print("already there, skipping")
        else:
            hm_db.add_unit(Home(u.info))        
hm_db.close_engine()






# import re
# user_agent = UserAgent()        
# headers = {"user-agent": user_agent.random}
# resp = requests.get("https://www.redfin.com/WA/Algona/230-4th-Ave-N-98001/home/365616", headers = headers)
# html = BeautifulSoup(resp.text, "lxml") 
# info = {}
# section = html.find("div", {"class": "HomeInfo inline-block"})
# top_stats = section.contents[0]
# bot_stats = section.contents[1]
# address = top_stats.contents[0].getText()
# info["address"] = address
# main_stats = top_stats.contents[1]
# sqft = int()
# per_sqft = int()
# for index, block in enumerate(main_stats):
#     if index == len(main_stats) - 1:
#         break
#     if len(block.contents) == 2:
#         value = block.contents[0].getText()
#         key = block.contents[1].getText()
#         info[key] = value
#     elif len(block.contents) == 1:
#         sub_b = block.contents[0]
#         sqft = sub_b.contents[0].getText()
#         per_sqft = re.findall(r"\d+", sub_b.contents[3].getText())
#         info["sqft"] = sqft
#         info["per_sqft"] = per_sqft

# stats_section = bot_stats.contents[1]
# more_info = bot_stats.contents[0].contents[0]
# stats = stats_section.find("span", {"class": "value"}).getText()
# info["stats"] = stats
# for i in range(1, len(more_info.contents)):
#     key = more_info.contents[i].find("span", {"class": "label"}).getText()
#     value = more_info.contents[i].find("span", {"class": "value"}).getText()
#     info[key] = value

# print(html)