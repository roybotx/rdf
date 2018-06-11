import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_all_wa_codes():
    url = "https://www.unitedstateszipcodes.org/wa/#zips-list"
    ua = UserAgent()
    headers = {"user-agent": ua.chrome}
    html = BeautifulSoup(requests.get(url, headers = headers).text, "lxml")
    cols = html.findAll("div", {"class": "list-group-item"})
    codes = set()
    for col in cols:
        codes.add(col.find("div").findAll("div")[0].getText().replace("\n", ""))
    return codes