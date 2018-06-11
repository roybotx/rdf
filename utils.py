import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import MySQLdb
import time


def __get_zipcodes_from_website():
    wa_url = "https://www.unitedstateszipcodes.org/wa/#zips-list"
    bs = get_bs(wa_url)
    list_group = bs.find("div", {"class": "list-group"}).findAll("div", {"class": "list-group-item"})
    codes = []
    for item in list_group:
        code_info = item.select("div[class*=\"col-xs-12 prefix-col\"]")
        code_info = [__process_code_info(content.getText()) for content in code_info]
        codes.append(code_info)
    return codes


def __process_code_info(info):
    info = re.sub("\s+", "", info)
    info = re.sub("AreaCode", "", info)
    return info


def get_bs(url):
    ua = UserAgent()
    headers = {"user-agent": ua.random}
    resp = requests.get(url, headers = headers)
    bs = BeautifulSoup(resp.text, "lxml")
    return bs


def __connect_to_db(database):
    db = MySQLdb.connect(host = "localhost", port = 3306, user = "root", passwd = "", db = database)
    return db


def execute_db(database, table_name, **fields_and_values):
    try:
        db = __connect_to_db(database)
        cur = db.cursor()
        sql = __build_save_query(table_name, **fields_and_values)
        cur.execute(sql)
        db.commit()
    except (MySQLdb.MySQLError, MySQLdb.Warning) as err:
        print(str(err))
        db.rollback()
    except Exception as err:
        print("Unknown Erros.\n" + str(err))
    finally:
        cur.close()
        db.close()    


def __build_save_query(table_name, **fields_and_values):
    if "entire_sql" in fields_and_values.keys():
        return fields_and_values["entire_sql"]
    sql = "insert ignore into " + table_name + " (" + ", ".join(fields_and_values["fields"]) + ") values "
    data = ""
    values = fields_and_values["values"]
    for value in values:
        if type(value) is list:
            data += "('" + "', '".join([v for v in value]) + "'),"
        else:
            data += "('" + value + "'),"
    data = data[: -1]
    sql += data
    return sql


def __build_select_query(table_name, fields, conditions = None):
    sql = "select "
    sql += "*" if fields[0] == "*" else ", ".join(fields) + " from " + table_name + " " + conditions
    return sql


def query_db(database, table_name, **fields_and_conditions):
    try:
        db = __connect_to_db(database)
        cur = db.cursor()
        sql = __build_select_query(table_name, fields_and_conditions["fields"], fields_and_conditions["conditions"])
        cur.execute(sql)
        return [row[0] for row in cur.fetchall()]
    except (MySQLdb.MySQLError, MySQLdb.Warning) as err:
        print(str(err))
        db.rollback()
    except Exception as err:
        print("Unknown Erros.\n" + str(err))
    finally:
        cur.close()
        db.close() 


def SLEEP_FOR_15_SEC():
    print("Sleeping for 15 seconds...")
    time.sleep(15)


# data = query_db("scraping", "zipcode", fields = ["zcode"], conditions = "where county = 'KingCounty'")
# print(len(data))

# codes = __get_zipcodes_from_website()
# sql = str()
# for code in codes:
#     sql += "set @ztype = '" + code[1] + "';update zipcode set code_type = @ztype where zcode = '" + code[0] + "';"
# execute_db("scraping", "zipcode", entire_sql = sql)