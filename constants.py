from fake_useragent import UserAgent
from enum import Enum

BASE_URL = "https://www.redfin.com"

LESS_THAN_ONE_WEEK_FILTER = "/filter/max-days-on-market=1wk"

SOLD_IN_THREE_MONTHS_FILTER = "/filter/include=sold-3mo"

SOLD_ALL_FILTER = "/filter/include=sold-all"

PENDING_FILTER = "/pending-listings"

ALL_HOMES_FILTER = "/filter/include=forsale+mlsfsbo+construction+fsbo+sold-all"

TEST_URL = "https://www.redfin.com/WA/Bothell/10818-NE-148th-Ln-98011/unit-P204/home/103957365"

ZIPCODE_SEARCH_URL = "https://www.redfin.com/zipcode/"

UA = UserAgent()

PROXY_TEST_URL = "http://ip.chinaz.com/getip.aspx"

TARGET_PROXY_URL = "https://free-proxy-list.net/anonymous-proxy.html"

WAIT_TIME = 5


class HOME_TYPE(Enum):
    ON_SALE = 0
    SOLD = 1
    PENDING = 2