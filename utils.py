import logging
import time
from bs4 import BeautifulSoup
import constants
import requests
from proxy_tool import Proxy


def config_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename="logs\log{}.log".format(time.strftime("%Y%m%d-%H%M%S")),
        filemode='w')
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def is_roboted(html):
    return "looks like our usage analysis algorithms think that you\n    might be a robot" in html


def make_call(url, retries):
    logger = logging.getLogger("utils.make_call")
    proxy_tool = Proxy()
    proxy_tool.get_proxies()
    headers = {"user-agent": constants.UA.random}
    for attempt in range(retries):
        try:
            resp = requests.get(
                url,
                headers=headers,
                proxies=proxy_tool.get_available_proxy(constants.WAIT_TIME))
            if is_roboted(resp.text):
                raise Exception("Got roboted...")
        except Exception as e:
            logger.error("Failed to get resp from {}.{}".format(url, str(e)))
            logger.error("Trying {} more time(s)...".format(retries - attempt))
        else:
            return BeautifulSoup(resp.text, "lxml")
