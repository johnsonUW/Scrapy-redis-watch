# -*- coding: utf-8 -*-
import re
from tools.yundama_requests import YDMHttp
import urllib.request

from ArticleSpider.utils.common import get_md5
import settings
from selenium import webdriver
try:
    import urlparse as parse
except:
    from urllib import parse

import scrapy
from scrapy.loader import ItemLoader
from items import JomaWatchItem,JomaWatchItemLoader


class JomaShopSpider(scrapy.Spider):
    name = "jomashop"
    allowed_domains = ["www.jomashop.com", "www.google.com"]
    start_urls = ['http://www.jomashop.com/watches.html?p=1']

    headers = {
        "HOST": "www.jomashop.com",
        "Referer": "http://www.jomashop.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="C:\\Users\\HTF\\Desktop\\search engine\\chromedriver.exe")
        super(JomaShopSpider,self).__init__()


    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        if 'http://www.google.com/intl/en/policies/' in all_urls:
            img = response.css("#recaptcha_challenge_image::attr(src)").extract_first("")
            with urllib.request.urlopen(img) as response, open(settings.IMAGES_STORE+"\captcha.jpg","wb") as out_file:
                data = response.read()
                out_file.write(data)

        #decaptcha
        captcha_code = self.decaptcha(settings.IMAGES_STORE+"\captcha.jpg")
        print("cccc",captcha_code)

        for url in all_urls:
            if url.startswith("http"):
                match_obj = re.match(".*jomashop.com.*watch.*html", url)
                if match_obj:
                    yield scrapy.Request(url=url, callback=self.parse_watches)
        next_url = ""
        for i in range(len(response.url) - 1):
            next_url += response.url[i]
        if (int(response.url[-1]) + 1 <= 720):
            next_url += str(int(response.url[-1]) + 1)
            yield  scrapy.Request(url=next_url,callback=self.parse)

    def parse_watches(self, response):

        item_loader = JomaWatchItemLoader(item=JomaWatchItem(), response=response)

        item_loader.add_css("watch_name",".product-name::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("price", "#final-price::text")
        item_loader.add_value("img_url", ".MagicToolboxContainer.selectorsBottom.minWidth img::attr(src)")

        item_loader.add_value("country", "US")
        item_loader.add_value("city", "N/A")
        item_loader.add_value("seller", "JomaShop")

        ship_status = response.css(".pdp-shipping-availability span .instock::text").extract_first("")
        if ship_status == "":
            ship_status = response.css(".pdp-shipping-availability span span::text").extract_first("")
        else:
            ship_status = ship_status + " " + response.css(".pdp-shipping-availability span .instock-ready::text").extract_first("")
        item_loader.add_value("ship_status", ship_status)

        watch_item = item_loader.load_item()

        yield watch_item

    def download_captcha(self, response):
        print(settings.IMAGES_STORE)
        with open(settings.IMAGES_STORE+"\captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()
        return

    def decaptcha(self,file):
        username = 'johnsondl'
        password = '9493943154'
        appid = 3591
        appkey = '8eeeff4c215953c27692796a7ec258bf'
        # 图片文件
        filename = file
        codetype = 5000

        timeout = 60
        if (username == 'username'):
            print('请设置好相关参数再测试')
        else:
            yundama = YDMHttp(username, password, appid, appkey)

            uid = yundama.login()
            print('uid: %s' % uid)

            uid = yundama.login()
            print('uid: %s' % uid)

            balance = yundama.balance()
            print('balance: %s' % balance)

            captcha_code = yundama.decode(filename, codetype, timeout)
            return captcha_code