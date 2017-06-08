# -*- coding: utf-8 -*-
import re
from redis import Redis
from scrapy_redis.spiders import RedisSpider
from urllib import parse

from ArticleSpider.items import Chrono24WatchItem, Chrono24WatchItemLoader

class chrono24PageSpider(RedisSpider):
    name = "chrono24_pages"
    allowed_domains = ["www.chrono24.com"]
    #start_url = "http://www.chrono24.com/watches/mens-watches--62.htm"
    redis_key = 'chrono24:page_urls'

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domans = filter(None, domain.split(','))
        super(chrono24PageSpider, self).__init__(*args, **kwargs)
        self.url = 'http://www.chrono24.com/'


    def parse(self, response):

        #item_loader = Chrono24WatchItemLoader(item=Chrono24WatchItem(), response=response)
        redis = Redis()
        next_url = response.css(".pagination.inline.pull-xs-none.pull-sm-right a::attr(href)").extract()[-1]
        match_obj = re.match(r".*\/watches.*\/.*\-\d+.htm", next_url)
        if next_url != "" and match_obj:
            redis.lpush("chrono24:page_urls", parse.urljoin(self.url,next_url))

        watch_nodes = response.css("#watches a")
        for watch_node in watch_nodes:
            watch_url = watch_node.css("::attr(href)").extract_first("")
            match_obj = re.match(r'\/.*id\d+.htm',watch_url)
            if match_obj:
                redis.lpush("chrono24:watch_urls", parse.urljoin(self.url,watch_url))

        return
