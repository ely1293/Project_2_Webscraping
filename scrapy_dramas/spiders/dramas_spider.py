import scrapy
from scrapy import Spider, Request
from dramas.items import DramasItem
import re
import math

class DramasSpider(Spider):
    name = 'dramas_spider'
    allowed_urls = ['https://www.mydramalist.com/']
    start_urls = ['https://mydramalist.com/shows/top']

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
        network = ', '.join(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[2]/div[2]/ul/li/a/text()').extract())

        actor1_patterns = ['//*[@id="content"]/div/div[2]/div/div[1]/div[2]/div[4]/ul/li[1]/div[2]/a/b/text()', '//*[@id="content"]/div/div[2]/div/div[1]/div[3]/div[4]/ul/li[1]/div[2]/a/b/text()', '//*[@id="content"]/div/div[2]/div/div[1]/div[4]/div[4]/ul/li[1]/div[2]/a/b/text()']

        for pattern in actor1_patterns:
            actor_1 = response.xpath(pattern).extract()
            if actor_1:
                break
            if not actor_1:
                continue

        actor2_patterns = ['//*[@id="content"]/div/div[2]/div/div[1]/div[4]/div[4]/ul/li[2]/div[2]/a/b/text()', '//*[@id="content"]/div/div[2]/div/div[1]/div[3]/div[4]/ul/li[2]/div[2]/a/b/text()', '//*[@id="content"]/div/div[2]/div/div[1]/div[2]/div[4]/ul/li[2]/div[2]/a/b/text()']

        for pattern in actor2_patterns:
            actor_2 = response.xpath(pattern).extract()
            if actor_2:
                break
            if not actor_2:
                continue

        rating = response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[1]/text()').extract_first().strip()
        users = int(''.join(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[1]/span/text()').re(r"(\d+,\d+)|(\d+)")).replace(",", "")) 
        watchers = int(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[4]/text()').extract_first().strip().replace(",", ""))
        
        ranking = int(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[2]/text()').re(r"(\d+)")[0])
        popularity = int(response.xpath('//*[@id="content"]/div/div[2]/div/div[2]/div/div[3]/div[2]/ul/li[3]/text()').re(r"(\d+)")[0])

        genre = ''.join(response.xpath('//li[@class="list-item p-a-0 show-genres"]//text()').extract()[1:]).strip()

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
        item['network'] = network
        try:
            item['actor_1'] = actor_1[0]
        except IndexError:
            item['actor_1'] = ''
        try:
            item['actor_2'] = actor_2[0]
        except IndexError:
            item['actor_2'] = ''
        item['rating'] = "" if 'N/A' in rating else float(rating)
        item['users'] = users
        item['watchers'] = watchers
        item['ranking'] = ranking
        item['popularity'] = popularity
        item['genre'] = genre
        item['tag'] = tag

        yield item