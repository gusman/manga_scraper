import scrapy
from scrapy_splash import SplashRequest

from manga_scraper.splash_script import LIST_CHAPTER
from manga_scraper.splash_script import OPEN_CHAPTER
from manga_scraper.items import MangaScraperItem


class BaseSpider(scrapy.Spider):
    name : str = NotImplemented
    start_urls : list = NotImplemented
    manga_title : str = NotImplemented

    base_url = 'https://mangajar.com'

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url,
                self.parse, 
                endpoint = 'execute',
                args={'lua_source': LIST_CHAPTER},
        )
    
    def parse(self, response):
        chapter_links = response.xpath('//li[@class="list-group-item chapter-item "]/a/@href').getall()
        chapter_names = response.xpath('//span[@class="chapter-title"]/text()').getall()

        list_cl = [ [name.strip(), self.base_url + link.strip()] for (name, link) in zip(chapter_names, chapter_links) ]

        for cl in list_cl[:1]:
            c_url = cl[1]
            yield SplashRequest(
                    c_url, 
                    self.chapter_parse, 
                    endpoint = 'execute',
                    args = {'lua_source' : OPEN_CHAPTER})
    
    def chapter_parse(self, response):
        img_srcs =  response.xpath('//div[@class="carousel-item active"]/img/@src').getall()
        img_srcs.extend(response.xpath('//div[@class="carousel-item"]/img/@data-src').getall())

        img_nums = response.xpath('//img/@data-number').getall()
        url_segments = str(response.url).rpartition('/') 

        item = MangaScraperItem()
        item['title'] = self.manga_title
        item['chapter'] = url_segments[len(url_segments) -1]
        item['pages'] = { img_num.strip() : img_src.strip() for img_num, img_src in zip(img_nums, img_srcs) }

        yield item

class RotlSpider(BaseSpider):
    name = 'rotl'
    start_urls = ['https://mangajar.com/manga/ruler-of-the-land-abs3VDC']
    manga_title = 'ruler-of-the-land'

class AodIISpider(BaseSpider):
    name = 'aod2'
    start_urls = ['https://mangajar.com/manga/diamond-no-ace-act-ii']
    manga_title = 'ace-of-diamond-2'

class KnyaSpider(BaseSpider):
    name = 'knya'
    start_urls = ['https://mangajar.com/manga/kimetsu-no-yaiba']
    manga_title = 'kinematsu-no-yaiba'
