from constants import TARGET_PROXY_URL
import requests
import re
from bs4 import BeautifulSoup
from itertools import cycle
import telnetlib
import logging
import time


class Proxy():
    def __init__(self, url_ = None):
        self.logger = logging.getLogger("Proxy")
        self.url = TARGET_PROXY_URL if url_ is None else url_

    def get_proxies(self):
        for i in range(5):
            try:
                resp = requests.get(self.url)
                html = BeautifulSoup(resp.text, "lxml")
                table = html.find("table", {"id": re.compile("proxylisttable")})
            except Exception as e:
                self.logger.warning("Couldn't get valid proxies, waiting for 10 seconds to refresh the site, retry {} more time(s)...".format(5 - i))
                time.sleep(10)
            else:
                self.proxies = set()
                if table is not None:
                    tbody = table.contents[1]
                    for tr in tbody.contents:
                        if "elite proxy" in tr.getText():
                            data = tr.contents
                            if "yes" in data[-2].getText():
                                prox = "{}:{}".format(data[0].getText(), data[1].getText())
                                self.proxies.add(prox)
                        if len(self.proxies) == 5:
                            break
                self.proxies = self.__test_proxy_availability()
                return self.proxies

    def __test_proxy_availability(self):
        proxy_pool = cycle(self.proxies)
        res = set()
        for i in range(0, len(self.proxies)):
            p = next(proxy_pool)
            try:
                telnetlib.Telnet(p.split(":")[0], port = p.split(":")[1], timeout = 3)
                res.add(p)
            except Exception:
                pass
                # self.logger.info("Connection Error, Fail. Removing proxy {}".format(p))
        return res

    def get_available_proxy(self, wait_time):
        if len(self.proxies) == 0:
            self.get_proxies()
        for p in self.proxies:
            ip = p.split(":")[0]
            port = p.split(":")[1]
            self.proxies.remove(p)
            try:
                telnetlib.Telnet(ip, port = port, timeout = 20)
                time.sleep(wait_time)
                return {"https": "https://" + p, "http": "http://" + p}
            except Exception as e:
                self.logger.info("{} is not available anymore, moving to next. {}".format(p, e))

            