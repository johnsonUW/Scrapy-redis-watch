# -*- coding: utf-8 -*-
import re
from redis import Redis
from scrapy_redis.spiders import RedisSpider
from urllib import parse

from ArticleSpider.items import xbiaoWatchItemLoader, xbiaoWatchItem


class xbiaoPageSpider(RedisSpider):
    name = "xbiao_pages"
    allowed_domains = ["www.xbiao.com","watch.xbiao.com"]
    #start_urls = ['http://watch.xbiao.com/']
    redis_key = 'xbiao:xbiao_urls'


    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domans = filter(None, domain.split(','))
        super(xbiaoPageSpider, self).__init__(*args, **kwargs)
        self.url = 'http://watch.xbiao.com/'

    def parse(self, response):

        next_url = response.css(".ar.next.right::attr(href)").extract_first("")
        redis = Redis()
        if next_url != "":
            redis.lpush('xbiao:xbiao_urls',parse.urljoin(self.url, next_url))
        watch_nodes = response.css(".watch-tile.wt a")
        for watch_node in watch_nodes:
            watch_url = watch_node.css("::attr(href)").extract_first("")
            match_obj = re.match(r'.*\/.*\d+.\/$', parse.urljoin("http://www.xbiao.com", watch_url))

            if match_obj:
                redis.lpush('xbiao:watch_urls', parse.urljoin("http://www.xbiao.com", watch_url))
        return




    def parse_watches(self, response):

        item_loader = xbiaoWatchItemLoader(item=xbiaoWatchItem(), response=response)

        item_loader.add_css("watch_name", ".zh_name::text")
        item_loader.add_value("url", response.url)
        item_loader.add_xpath("price", "/html/body/div[4]/div[2]/div[1]/div[3]/ul[2]/li[1]/span/text()")
        item_loader.add_css("img_url", ".big-pic img::attr(src)")
        item_loader.add_value("country", "中国")
        item_loader.add_value("city", "上海")
        item_loader.add_xpath("seller", "/html/body/div[4]/div[2]/div[2]/div[1]/ul/li[1]/a/text()")
        item_loader.add_value("ship_status", "Buy in store")

        watch_item = item_loader.load_item()

        return watch_item
