# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader.processors import MapCompose
import datetime


class ProductItem(Item):
    datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    collection = 'jingdong-{}'.format(datetime_str)

    keyword = Field()
    page = Field()
    title = Field()
    price = Field()
    seller = Field()
    comment = Field(
        input_processor=MapCompose(str.strip, (lambda i: i.replace('+', '')), (lambda i: str(int(10000*float(i.replace('万', '')))) if '万' in i else i)),
    )
    img_url = Field()
