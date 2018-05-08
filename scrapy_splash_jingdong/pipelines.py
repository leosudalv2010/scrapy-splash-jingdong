# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import pymongo


class NoFieldFilterPipeline(object):
    def process_item(self, item, spider):
        if not item.get('title'):
            raise DropItem('Found item without title')
        if not item.get('seller'):
            raise DropItem('Found item without seller')
        return item


class DuplicateFilterPipeline(object):
    def __init__(self):
        self.item_seen = []

    def process_item(self, item, spider):
        if (item['title'], item['seller']) in self.item_seen:
            raise DropItem('Found duplicate item')
        else:
            self.item_seen.append((item['title'], item['seller']))
        return item


class MongoPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client['mydb']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[item.collection].insert_one(dict(item))
        return item
