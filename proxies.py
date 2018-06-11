import MySQLdb as db
from urllib.request import Request
from urllib.request import ProxyHandler
from urllib.request import build_opener
from urllib.request import install_opener
from urllib.request import urlopen
from lxml import etree
from bs4 import BeautifulSoup
import re


def get_html(url):
    request = Request(url)
    request.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
    )
    html = urlopen(request)
    return html.read()


#获取快代理上可用的HTTPS代理IP
def fetch_kuaidaili():
    startUrl = 'http://www.kuaidaili.com/proxylist/'
    proxys = []
    for i in range(1, 11):
        url = startUrl + str(i) + '/'
        html = etree.HTML(get_html(url))
        trs = html.xpath('//*[@id="index_free_list"]/table/tbody/tr')
        for line in range(10):
            td_type = trs[line].xpath('td[4]/text()')[0]
            if 'HTTPS' in td_type:  #判断是否为HTTPS代理，不是则不抓取
                td_speed = trs[line].xpath('td[7]/text()')[0][:-1:]
                if float(td_speed) < 1.0:
                    td_ip = trs[line].xpath('td[1]/text()')[0]
                    td_port = trs[line].xpath('td[2]/text()')[0]
                    ip = td_ip + ':' + str(td_port)
                    proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print('from kuaidaili...%s' % len(useFullIp))
    return useFullIp


#kxdaili,获取可用的HTTPS代理IP
def fetch_kxdaili():
    startUrl = 'http://www.kxdaili.com/ipList/'  #地址随时可能变动需要添加处理机制
    proxys = []
    for i in range(1, 11):
        url = startUrl + str(i) + '.html'
        html = etree.HTML(get_html(url))
        trs = html.xpath('//*[@id="nav_btn01"]/div[5]/table/tbody/tr')
        for line in range(len(trs)):
            td_type = trs[line].xpath('td[4]/text()')[0]
            if 'HTTPS' in td_type:  #判断是否为HTTPS代理，不是则不抓取
                td_speed = trs[line].xpath('td[5]/text()')[0].split('.')[0]
                if int(td_speed) < 1:
                    td_ip = trs[line].xpath('td[1]/text()')[0]
                    td_port = trs[line].xpath('td[2]/text()')[0]
                    ip = td_ip + ':' + str(td_port)
                    proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))

    print('from kxdaili...%s' % len(useFullIp))
    # print useFullIp
    return useFullIp


#这个瑶瑶代理可用的IP太少!!!
def fetch_yaoyaodaili():
    startUrl = 'http://www.httpsdaili.com/free.asp?page='
    proxys = []
    for i in range(1, 8):
        url = startUrl + str(i)
        html = etree.HTML(get_html(url))
        trs = html.xpath('//*[@id="list"]/table/tbody/tr')
        for line in range(len(trs)):
            td_type = trs[line].xpath('td[4]/text()')[0]
            if 'HTTPS' in td_type:
                td_speed = trs[line].xpath('td[6]/text()')[0]
                if '0秒' == td_speed:
                    td_ip = trs[line].xpath('td[1]/text()')[0]
                    td_port = trs[line].xpath('td[2]/text()')[0]
                    ip = td_ip + ':' + td_port
                    proxys.append(ip)

    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print('from httpsdaili...%s' % len(useFullIp))
    return useFullIp


#获取西刺速度小于5秒的HTTPS代理
def fetch_xici():
    startUrl = 'http://www.xicidaili.com/wn/1'
    proxys = []
    html = etree.HTML(get_html(startUrl))
    tables = html.xpath('//table[@id="ip_list"]')
    trs = tables[0].xpath('tr')
    for line in trs[1:]:
        td_type = line.xpath('td[6]/text()')[0].strip()
        if 'HTTPS' == td_type:
            td_speed = line.xpath('td[7]/div/@title')[0].strip()[:-1]
            if float(td_speed) < 5:
                td_ip = line.xpath('td[2]/text()')[0].strip()
                td_port = line.xpath('td[3]/text()')[0].strip()
                ip = td_ip + ':' + td_port
                proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print("from xici ... %s" % len(useFullIp))
    return useFullIp


#年少HTTPS代理，国外代理,用不着..
def fetch_nianshao():
    startUrl = 'http://www.nianshao.me/?stype=2&page='
    proxys = []
    for i in range(1, 50):
        url = startUrl + str(i)
        html = etree.HTML(get_html(url))
        trs = html.xpath('//tr')
        for line in trs[1:]:
            td_type = line.xpath('td[5]/text()')[0].strip()
            if "HTTPS" == td_type:
                td_speed = line.xpath('td[6]/div/div/@style')[0].strip()[6:8]
                if int(td_speed) >= 70:
                    td_ip = line.xpath('td[1]/text()')[0].strip()
                    td_port = line.xpath('td[2]/text()')[0].strip()
                    ip = td_ip + ":" + td_port
                    proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print("from nianshao ... %s" % len(useFullIp))
    print(useFullIp)


#360代理IPHTTPS高匿部分
def fetch_swei360():
    startUrl = 'http://www.swei360.com/free/?page='
    proxys = []
    for i in range(1, 8):
        url = startUrl + str(i)
        html = etree.HTML(get_html(url))
        trs = html.xpath('//tr')
        for line in trs[1:]:
            td_type = line.xpath('td[4]/text()')[0].strip()
            if "HTTPS" == td_type:
                td_hide = line.xpath('td[3]/text()')[0].strip()
                if '高匿' in td_hide:
                    td_speed = line.xpath('td[6]/text()')[0].strip()[:-1]
                    if int(td_speed) <= 5:
                        td_ip = line.xpath('td[1]/text()')[0].strip()
                        td_port = line.xpath('td[2]/text()')[0].strip()
                        ip = td_ip + ":" + td_port
                        proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print("from swei360 ... %s" % len(useFullIp))
    return useFullIp


#获取ip3366的7页HTTPS代理IP
def fetch_ip3366():
    startUrl = 'http://www.ip3366.net/free/?stype=1&page='
    proxys = []
    for i in range(1, 8):
        url = startUrl + str(i)
        html = etree.HTML(get_html(url))
        trs = html.xpath('//tr')
        for line in trs[1:]:
            td_type = line.xpath('td[4]/text()')[0].strip()
            if "HTTPS" == td_type:
                td_speed = line.xpath('td[6]/text()')[0].strip()[:-1]
                if int(td_speed) <= 5:
                    td_ip = line.xpath('td[1]/text()')[0].strip()
                    td_port = line.xpath('td[2]/text()')[0].strip()
                    ip = td_ip + ":" + td_port
                    proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print("from ip3366 ...%s" % len(useFullIp))
    return useFullIp


#提取秘密代理IP前4页的代理
def fetch_mimiip():
    startUrl = 'http://www.mimiip.com/gngao/'
    proxys = []
    for i in range(1, 5):
        url = startUrl + str(i)
        html = etree.HTML(get_html(url))
        trs = html.xpath('//tr')
        for line in trs[1:]:
            td_type = line.xpath('td[5]/text()')[0].strip()
            if "HTTPS" == td_type:
                td_speed = line.xpath('td[6]/div/@style')[0].strip()[6:-2]
                if int(td_speed) >= 70:
                    td_ip = line.xpath('td[1]/text()')[0].strip()
                    td_port = line.xpath('td[2]/text()')[0].strip()
                    ip = td_ip + ":" + td_port
                    proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print("from mimiip ...%s" % len(useFullIp))
    return useFullIp


#获取IP巴士前6页
def fetch_ip84():
    startUrl = 'http://ip84.com/gn/'
    proxys = []
    for i in range(1, 7):
        url = startUrl + str(i)
        html = etree.HTML(get_html(url))
        trs = html.xpath('//tr')
        for line in trs[1:]:
            td_type = line.xpath('td[5]/text()')[0].strip()
            if "HTTPS" == td_type:
                td_speed = line.xpath('td[6]/text()')[0].strip()[:-1]
                if int(td_speed) <= 5:
                    td_ip = line.xpath('td[1]/text()')[0].strip()
                    td_port = line.xpath('td[2]/text()')[0].strip()
                    ip = td_ip + ":" + td_port
                    proxys.append(ip)
    useFullIp = testIp(map(lambda x: x.strip(), proxys))
    print("from ip84 ...%s" % len(useFullIp))
    return useFullIp


#安小莫匿名IP提取api,提取最大800个
def fetch_66ip():
    startUrl = 'http://www.66ip.cn/nmtq.php?getnum=800&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=1&api=66ip'
    # driver = webdriver.PhantomJS()
    # driver.get(startUrl)
    # soup = BeautifulSoup(driver.page_source,"lxml")
    soup = BeautifulSoup(get_html(startUrl))
    body = soup.body.find_all(text=re.compile('\d+\.\d+\.\d+\.\d+:\d+'))
    body = map(lambda x: x.strip(), body)
    useFullIp = testIp(body)
    print('from 66ip...%s' % len(useFullIp))
    return useFullIp


#测试代理IP是否可用,传入ip列表，返回可用ip列表
def testIp(ip_list):
    useFullIp = []
    for ip in ip_list:
        # proxy_handler = ProxyHandler({"https": ip})
        # opener = build_opener(proxy_handler)
        # install_opener(opener)
        # response = urlopen("https://www.baidu.com/", timeout=10)
        # if response.getcode() == 200:
        useFullIp.append(ip)
    return useFullIp


#写入数据库
def ip2db(iplist):
    con = db.connect(host = "localhost", user = "root", passwd = '', db = 'scraping', charset='utf8', port = 3306)
    cur = con.cursor()
    # cur.execute("truncate table xiciproxy") #写入数据库前清空数据库
    for ip in iplist:
        try:
            cur.execute("insert into ipproxies(ip) values('%s')" % (ip))
        except Exception as e:
            print("Insert ip Error %s" % e)
    print('Insert Success...')
    con.commit()
    cur.close()
    con.close()
    return True


def NEWHTTPS():
    # ip1 = fetch_kuaidaili()
    # ip2 = fetch_kxdaili()
    # ip3 = fetch_yaoyaodaili()
    # ip4 = fetch_66ip()
    # ip5 = fetch_xici()
    # ip6 = fetch_swei360()
    # ip7 = fetch_ip3366()
    ip8 = fetch_mimiip()
    # ip9 = fetch_ip84()
    https_list = list(set(ip8))
    ip2db(map(lambda x: x.strip(), https_list))
    print('HTTPS Proxy Ip is OK ...%s' % len(https_list))


if __name__ == '__main__':
    NEWHTTPS()
