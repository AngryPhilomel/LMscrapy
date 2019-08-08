import scrapy
from urllib.parse import urljoin

allItem = []
allObject = []

with open('text.txt', 'w', encoding='utf-8') as file_out:
				file_out.write('Наименование; Артикул; Цена\n')
				file_out.close()

class LMSpider(scrapy.Spider):
	name = "lm_spider"
	start_urls = ['https://leroymerlin.ru/catalogue/']

	def parse(self, response):
		
		for category in response.xpath(
			'//div[@class="title"]/a/@href').extract():
			url = urljoin(response.url, category)
			print (url)
			yield response.follow(url, callback=self.parse_subcategory)


	def parse_subcategory(self, response):
		for subcategory in response.xpath('//div[@class="items"]/ul/li/a/@href').extract():
			url = urljoin(response.url, subcategory)
			print(url)
			yield response.follow(url, callback=self.parse_item)


	def parse_item(self, response):

		SET_SELECTOR = '.ui-sorting-cards'
		
		for item in response.css(SET_SELECTOR):
			
			NAME_SELECTOR = '.product-name a ::text'
			PRICE_SELECTOR = 'span.main-value-part ::text'
			ATICLE_SELECTOR = '.madein__text ::text'
			IMAGE_SELECTOR = ".ui-product-card__img picture img ::attr(src)"
		
			yield allItem.append({
				'name': item.css(NAME_SELECTOR).extract_first(),
				'price': item.css(PRICE_SELECTOR).extract_first(),
				'aticle': item.css(ATICLE_SELECTOR).extract(),
				'image': item.css(IMAGE_SELECTOR).extract_first()
				})
			

			

		NEXT_PAGE_SELECTOR = '.next-paginator-button-wrapper a ::attr(href)'
		next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
		if next_page:
			yield scrapy.Request(
				response.urljoin(next_page),
				callback=self.parse)
		else:
			for i in range(0, len(allItem)):
				name = allItem[i].get('name')
				price = allItem[i].get('price')
				aticle = allItem[i].get('aticle')
				image = allItem[i].get('image')
				allObject.append(LMItem(name, price, aticle, image))

			with open('text.txt', 'a', encoding='utf-8') as file_out:
				for n in allObject:
					print (n)
					try:
						file_out.write(n.save())
						file_out.write('\n')
					else:
						allItem.clear()
						allObject.clear()	
					finally:
						allItem.clear()
						allObject.clear()
					
					

			

class LMItem():
	def __init__(self, name, price, aticle, image):
		self.name = name
		self.price = price
		self.aticle = aticle
		self.image = image

	def save(self):
		return('{}; {}; {}'.format(self.name, self.aticle[1], self.price))

	def __repr__(self):
		return('Наименование: {}, Артикул: {}, Цена: {}'.format(self.name, self.aticle[1], self.price))
