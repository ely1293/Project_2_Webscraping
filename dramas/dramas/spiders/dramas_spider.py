# import scrapy
# from scrapy import Spider, Request
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor
# from dramas.items import DramasItem
# import re
# import math

# class DramasSpider(CrawlSpider):
#     name = 'dramas_spider'
#     allowed_urls = ['https://www.mydramalist.com/']
#     start_urls = ['https://www.mydramalist.com/shows/top']

#     rules = (
#         # Extract links matching 'category.php' (but not matching 'subsection.php')
#         # and follow links from them (since no callback means follow=True by default).
#         Rule(LinkExtractor(allow=('top?page='))),

#         # Extract links matching 'item.php' and parse them with the spider's method parse_item
#         Rule(LinkExtractor(), callback='parse_drama_page'),
#     )


#     def parse(self, response):
#         next_url = response.xpath('//li[@class="page-item next"]/a/@href')

#         yield from self.parse_result_page(response)
       
#         if next_url:
#             path = next_url.extract_first()
#             next_page = response.urljoin(path)
#             print("Found url: {}".format(next_page))
#             yield scrapy.Request(next_page, callback=self.parse)


#     def parse_result_page(self, response):
#         drama_urls = response.xpath('//h6[@class="text-primary title"]/a/@href').extract()
#         drama_urls = [f'https://www.mydramalist.com{url}' for url in drama_urls]
#         for url in drama_urls:
#             print("Starting to scrape drama url: " + url)
#             yield Request(url=url, callback=self.parse_drama_page)


#     def parse_drama_page(self, response):

#         print("Response: " + str(response))

#         title = response.xpath('.//span[@itemprop="name"]/text()').extract_first()

#         if title:
#             print("Extracting drama: " + title)
#             country = response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[2]/text()').extract_first().strip()
#             episodes = int(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[3]/text()').extract_first().strip())
#             start_date = response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[4]/text()').extract_first().split("-")[0].strip()
#             end_date = response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[4]/text()').extract_first().split("-")[1].strip()
#             network = ''.join(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[6]//text()').extract()[1:]).strip()
#             rating = float(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[1]/text()').extract_first().strip())
#             users = int(''.join(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[1]/span/text()').re(r"\(scored by (\d+,)?(\d+) users\)")).replace(",", ""))
#             watchers = int(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[4]/text()').extract_first().strip().replace(",", ""))
#             reviews = int(response.xpath('//*[@id="show-detailsxx"]/div[1]/div[2]/div[4]/a/text()').re(r"(\d+)")[0])
#             genre = ''.join(response.xpath('//li[@class="list-item p-a-0 show-genres"]//text()').extract()[1:]).strip()

#             item = DramasItem()
#             item['title'] = title
#             item['country'] = country
#             item['episodes'] = episodes
#             item['start_date'] = start_date
#             item['end_date'] = end_date
#             item['network'] = network
#             item['rating'] = rating
#             item['users'] = users
#             item['watchers'] = watchers
#             item['reviews'] = reviews
#             item['genre'] = genre

#             yield item



import scrapy
from scrapy import Spider, Request
from dramas.items import DramasItem
import re
import math

class DramasSpider(Spider):
    name = 'dramas_spider'
    allowed_urls = ['https://www.mydramalist.com/']
    start_urls = ['https://mydramalist.com/search?adv=titles&ty=68&st=1&so=top&page=1']

    def parse(self, response):
        next_url = response.xpath('//li[@class="page-item next"]/a/@href')

        yield from self.parse_result_page(response)
        
        if next_url:
            path = next_url.extract_first()
            next_page = response.urljoin(path)
            # print("Found url: {}".format(next_page))
            yield scrapy.Request(next_page, callback=self.parse)


    def parse_result_page(self, response):
        drama_urls = response.xpath('//h6[@class="text-primary title"]/a/@href').extract()
        drama_urls = [f'https://www.mydramalist.com{url}' for url in drama_urls]
        for url in drama_urls:
            # print("Starting to scrape drama url: " + url)
            yield Request(url=url, callback=self.parse_drama_page)


    def parse_drama_page(self, response):

        # print("Response: " + str(response))

        title = response.xpath('.//span[@itemprop="name"]/text()').extract_first()
        country = response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[2]/text()').extract_first().strip()
        episodes = int(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[3]/text()').extract_first().strip())
        date_aired = response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[4]/text()').extract_first().strip()
        # network = ''.join(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li[6]//text()').extract()[1:]).strip()
        network = ', '.join(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li/a/text()').extract())
        
        actor_patterns = ['//*[@id="content"]/div/div[2]/div/div[1]/div[2]/div[4]/ul/li/div[2]/a/b/text()', '//*[@id="content"]/div/div[2]/div/div[1]/div[3]/div[4]/ul/li/div[2]/a/b/text()']
        for actor_pattern in actor_patterns:
            actor = response.xpath(actor_pattern).extract()
            if actor:
                break
            if not actor:
                continue

        # actor_1 = response.xpath('//*[@id="content"]/div/div[2]/div/div[1]/div[2]/div[4]/ul/li/div[2]/a/b/text()').extract_first()
        # actor_2 = response.xpath('//*[@id="content"]/div/div[2]/div/div[1]/div[2]/div[4]/ul/li/div[2]/a/b/text()').extract()
        rating = response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[1]/text()').extract_first().strip()
        users = int(''.join(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[1]/span/text()').re(r"(\d+,\d+)|(\d+)")).replace(",", "")) 
        watchers = int(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[4]/text()').extract_first().strip().replace(",", ""))
        # reviews = int(response.xpath('//*[@id="show-detailsxx"]/div[1]/div[2]/div[4]/a/text()').re(r"(\d+)")[0])
        genre = ''.join(response.xpath('//li[@class="list-item p-a-0 show-genres"]//text()').extract()[1:]).strip()
        # tag = ', '.join(response.xpath('//*[@id="show-detailsxx"]/div[4]/ul[1]/li[4]/span/a/text()').extract())
        # tag_else = ', '.join(response.xpath('//*[@id="show-detailsxx"]/div[4]/ul[1]/li[7]/span/a/text()').extract())

        patterns = ['//*[@id="show-detailsxx"]/div[4]/ul[1]/li[7]/span/a/text()', '//*[@id="show-detailsxx"]/div[4]/ul[1]/li[4]/span/a/text()', '//*[@id="show-detailsxx"]/div[4]/ul[1]/li[6]/span/a/text()', '//*[@id="show-detailsxx"]/div[4]/ul[1]/li[5]/span/a/text()']

        for pattern in patterns:
            tag = ', '.join(response.xpath(pattern).extract())
            if tag:
                break
            if not tag:
                continue

        item = DramasItem()
        item['title'] = title
        item['country'] = country
        item['episodes'] = episodes
        item['date_aired'] = date_aired
        # item['end_date'] = end_date
        # item['network'] = '' if any(x in network for x in ['min.', 'Not', 'older']) else network
        item['network'] = network
        item['actor_1'] = actor[0]
        try:
            item['actor_2'] = actor[1]
        except IndexError:
            item['actor_2'] = ''
        item['rating'] = "" if 'N/A' in rating else float(rating)
        item['users'] = users
        item['watchers'] = watchers
        # item['reviews'] = reviews
        item['genre'] = genre
        item['tag'] = tag

        yield item


