# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from urllib.parse import quote
from scrapy.loader import ItemLoader
from scrapy_splash_jingdong.items import ProductItem
from scrapy.loader.processors import Join, MapCompose


class JingdongSpider(scrapy.Spider):
    name = 'jingdong'
    allowed_domains = ['jd.com']
    scrip = """
    function main(splash)
      splash.images_enabled = false
      assert(splash:go(splash.args.url))
      assert(splash:wait(splash.args.wait))
      js = string.format("document.querySelector('#J_bottomPage > span.p-skip > input').value=%d; \
           document.querySelector('#J_bottomPage > span.p-skip > a').click()", splash.args.page)
      splash:evaljs(js)
      splash:set_viewport_full()
      assert(splash:wait(splash.args.wait))
      return splash:html()
    end
    """

    def start_requests(self):
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = 'https://search.jd.com/Search?keyword={}&enc=utf-8'.format(quote(keyword))
                yield SplashRequest(url, self.parse, endpoint='execute', args={
                    'wait': 8,
                    'page': page,
                    'lua_source': self.scrip,
                }, meta={
                    'keyword': keyword,
                    'page': page,
                })

    def parse(self, response):
        products = response.xpath('//ul[starts-with(@class, "gl-warp")]/li')
        keyword = response.meta.get('keyword')
        page = str(response.meta.get('page'))
        for product in products:
            loader = ItemLoader(item=ProductItem())
            loader.default_input_processor = MapCompose(str.strip)
            loader.default_output_processor = Join()
            loader.add_value('keyword', keyword)
            loader.add_value('page', page)
            loader.add_value('title', product.xpath('.//div[starts-with(@class,"p-name")]/a/em//text()').extract())
            loader.add_value('price', product.xpath('.//div[starts-with(@class,"p-price")]/strong/i/text()').extract())
            loader.add_value('seller', product.xpath('.//div[starts-with(@class,"p-shop")]/span/a/text()').extract())
            if not product.xpath('.//div[starts-with(@class,"p-shop")]/span/a/text()').extract():
                loader.add_value('seller', '京东自营')
            loader.add_value('comment', product.xpath('.//div[starts-with(@class,"p-commit")]/strong/a/text()').extract())
            loader.add_value('img_url', product.xpath('.//div[starts-with(@class,"p-img")]/a/img/@src').extract())
            yield loader.load_item()
        self.logger.info('Page {} of {} was completed'.format(page, keyword))


