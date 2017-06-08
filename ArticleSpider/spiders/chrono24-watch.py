# -*- coding: utf-8 -*-
import re
from scrapy_redis.spiders import RedisSpider
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import Chrono24WatchItem, Chrono24WatchItemLoader


class chrono24WatchSpider(RedisSpider):
    name = "chrono24_watch"
    allowed_domains = ["www.chrono24.com"]
    redis_key = 'chrono24:watch_urls'


    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domans = filter(None, domain.split(','))
        super(chrono24WatchSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        item_loader = Chrono24WatchItemLoader(item=Chrono24WatchItem(), response=response)

        item_loader.add_xpath("watch_name",
                              "// *[ @ id = 'anti-flicker'] / div[6] / div / section[1] / div[1] / div[3] / div / h1/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("price",
                              "//*[@id='anti-flicker']/div[6]/div[1]/section[1]/div[1]/div[4]/div[2]/div[1]/span/text()[last()]")
        img_url = response.css(".detail-images .detail-image div div::attr(style)").extract_first("")
        build_url = False
        res = ""
        for s in img_url:
            if s == "(":
                build_url = True
            elif s == ")":
                build_url = False
            if build_url:
                res += s
        res = res.replace("(", "")
        item_loader.add_value("img_url", res)
        country = response.xpath(
            "//*[@id='anti-flicker']/div[6]/div[1]/section[1]/div[1]/div[4]/div[2]/div[2]/div/div[2]/div[1]/span/text()").extract_first(
            "").split("-")[0].replace(" ", "")
        if len(response.xpath(
            "//*[@id='anti-flicker']/div[6]/div[1]/section[1]/div[1]/div[4]/div[2]/div[2]/div/div[2]/div[1]/span/text()").extract_first(
            "").split("-")) >= 2 :
            city = response.xpath(
                "//*[@id='anti-flicker']/div[6]/div[1]/section[1]/div[1]/div[4]/div[2]/div[2]/div/div[2]/div[1]/span/text()").extract_first(
                "").split("-")[1].replace(" ", "")
        else:
            city = ""
        item_loader.add_value("country", country)
        item_loader.add_value("city", city)
        item_loader.add_css("seller", ".m-t-0.link-inverted.link-merchant-name .m-r-1::text")
        ship_status = response.xpath(
            "//*[@id='anti-flicker']/div[6]/div[1]/section[1]/div[1]/div[4]/ div[2] / div[1] / p / small / text()").extract_first(
            "")
        if ship_status == "":
            ship_status = response.xpath(
                "//*[@id='anti-flicker']/div[6]/div/section[1]/div[1]/div[4]/div[2]/div[1]/p/span/text()").extract_first(
                "")
        item_loader.add_value("ship_status", ship_status)

        watch_item = item_loader.load_item()

        return watch_item


