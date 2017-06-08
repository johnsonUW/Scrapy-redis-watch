# -*- coding: utf-8 -*-
import re
from scrapy_redis.spiders import RedisSpider
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import xbiaoWatchItemLoader, xbiaoWatchItem


class xbiaoWatchSpider(RedisSpider):
    name = "xbiao_watch"
    allowed_domains = ["www.xbiao.com","watch.xbiao.com"]
    redis_key = 'xbiao:watch_urls'


    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domans = filter(None, domain.split(','))
        super(xbiaoWatchSpider, self).__init__(*args, **kwargs)


    def parse(self, response):

        item_loader = xbiaoWatchItemLoader(item=xbiaoWatchItem(), response=response)

        item_loader.add_css("watch_name", ".zh_name::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("price", "/html/body/div[4]/div[2]/div[1]/div[3]/ul[2]/li[1]/span/text()")
        item_loader.add_css("img_url", ".big-pic img::attr(src)")
        item_loader.add_value("country", "中国")
        item_loader.add_value("city", "上海")
        item_loader.add_xpath("seller", "/html/body/div[4]/div[2]/div[2]/div[1]/ul/li[1]/a/text()")
        item_loader.add_value("ship_status", "Buy in store")

        watch_item = item_loader.load_item()

        return watch_item
