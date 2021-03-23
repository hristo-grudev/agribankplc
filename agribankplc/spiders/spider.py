import scrapy

from scrapy.loader import ItemLoader

from ..items import AgribankplcItem
from itemloaders.processors import TakeFirst


class AgribankplcSpider(scrapy.Spider):
	name = 'agribankplc'
	start_urls = ['https://agribankplc.com/newsroom/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="list_wrap"]/ul/li')
		for post in post_links:
			url = post.xpath('.//div[@class="li_t"]/a/@href').get()
			date = post.xpath('.//div[@class="dt"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//a[@class="nextpostslink"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//article//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=AgribankplcItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
