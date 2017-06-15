# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


from models.es_types import EnglishType, ChineseType


from elasticsearch_dsl.connections import connections
es = connections.create_connection(EnglishType._doc_type.using)
es2 = connections.create_connection(ChineseType._doc_type.using)

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    pass



def get_price(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums



def gen_suggests_eng(index, info_tuple):

    used_words = set()
    suggests = []
    for text in info_tuple:
        if text:

            words = es.indices.analyze(index=index, analyzer="standard", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words)})

    return suggests

def gen_suggests_chn(index, info_tuple):

    used_words = set()
    suggests = []
    for text in info_tuple:
        if text:

            words = es2.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words)})

    return suggests

class Chrono24WatchItemLoader(ItemLoader):

    default_output_processor = TakeFirst()


class Chrono24WatchItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    watch_name = scrapy.Field()
    price = scrapy.Field()
    img_url = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    seller = scrapy.Field()
    ship_status = scrapy.Field()


    def save_to_es(self):
        watches = EnglishType()
        if 'url' in self and 'watch_name' in self and 'price' in self and 'img_url' in self and 'country' in self and 'city' in self and 'seller' in self and 'ship_status' in self:
            watches.url = self['url']
            watches.watch_name = self['watch_name']
            watches.price = self['price']
            watches.img_url = self['img_url']
            watches.country = self['country']
            watches.city = self['city']
            watches.seller = self['seller']
            watches.ship_status = self['ship_status']
            watches.meta.id = self["url_object_id"]

            watches.suggest = gen_suggests_eng(EnglishType._doc_type.index, (watches.watch_name, 10))

            watches.save()


        return


class JomaWatchItemLoader(ItemLoader):

    default_output_processor = TakeFirst()

class JomaWatchItem(scrapy.Item):

    url = scrapy.Field()
    url_object_id = scrapy.Field()
    watch_name = scrapy.Field()
    price = scrapy.Field()
    img_url = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    seller = scrapy.Field()
    ship_status = scrapy.Field()

    def save_to_es(self):
        watches = EnglishType()
        if self['url'] and self['watch_name'] and self['price'] and self['img_url'] and self['country'] and self[
            'city'] and self['seller'] and self['ship_status']:
            watches.url = self['url']
            watches.watch_name = self['watch_name']
            watches.price = self['price']
            watches.img_url = self['img_url']
            watches.country = self['country']
            watches.city = self['city']
            watches.seller = self['seller']
            watches.ship_status = self['ship_status']
            watches.meta.id = self["url_object_id"]

            watches.suggest = gen_suggests_eng(EnglishType._doc_type.index, (watches.watch_name, 10))

            watches.save()



class xbiaoWatchItemLoader(ItemLoader):

    default_output_processor = TakeFirst()


class xbiaoWatchItem(scrapy.Item):

    url = scrapy.Field()
    url_object_id = scrapy.Field()
    watch_name = scrapy.Field()
    price = scrapy.Field(
        input_processor = MapCompose(get_price)
    )
    img_url = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    seller = scrapy.Field()
    ship_status = scrapy.Field()

    def save_to_es(self):
        watches = ChineseType()
        if self['url'] and self['watch_name'] and self['price'] and self['img_url'] and self['country'] and self[
            'city'] and self['seller'] and self['ship_status']:
            watches.url = self['url']
            watches.watch_name = self['watch_name']
            watches.price = self['price']
            watches.img_url = self['img_url']
            watches.country = self['country']
            watches.city = self['city']
            watches.seller = self['seller']
            watches.ship_status = self['ship_status']
            watches.meta.id = self["url_object_id"]

            watches.suggest = gen_suggests_chn(EnglishType._doc_type.index, (watches.watch_name, 10))

            watches.save()
