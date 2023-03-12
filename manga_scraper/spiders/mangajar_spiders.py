import scrapy
from scrapy_splash import SplashRequest

from manga_scraper.items import MangaScraperItem
from manga_scraper.splash_script import LIST_CHAPTER, OPEN_CHAPTER


class BaseSpider(scrapy.Spider):
    name: str = NotImplemented
    start_urls: list = NotImplemented
    manga_title: str = NotImplemented

    base_url = "https://mangajar.com"

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url,
                self.parse,
                endpoint="execute",
                args={"lua_source": LIST_CHAPTER},
            )

    def parse(self, response):
        chapter_links = response.xpath(
            '//li[@class="list-group-item chapter-item "]/a/@href'
        ).getall()

        chapter_names = response.xpath('//span[@class="chapter-title"]/text()').getall()

        list_cl = [
            [name.strip(), self.base_url + link.strip()]
            for (name, link) in zip(chapter_names, chapter_links)
        ]

        n_last_chapter = self.settings["N_LAST_CHAPTER"]

        for cl in list_cl[:n_last_chapter]:
            c_url = cl[1]
            yield SplashRequest(
                c_url,
                self.chapter_parse,
                endpoint="execute",
                args={"lua_source": OPEN_CHAPTER},
            )

    def chapter_parse(self, response):
        srcs = response.xpath(
            '//div[@class="mt-1 d-flex flex-column align-items-center chapter-images"]/img/@src'
        ).getall()

        data_srcs = response.xpath(
            '//div[@class="mt-1 d-flex flex-column align-items-center chapter-images"]/img/@data-src'
        ).getall()

        img_srcs = srcs
        img_srcs.extend(data_srcs)

        # Strip the image sources text
        img_srcs = [img_src.strip() for img_src in img_srcs]

        # Filter server local sources
        img_srcs = [img_src for img_src in img_srcs if img_src.startswith("http")]

        # Retrieve page number
        img_nums = response.xpath("//img/@data-number").getall()
        img_nums = [img_num.strip() for img_num in img_nums]

        url_segments = str(response.url).rpartition("/")

        # Populate the item for image download pipeline
        item = MangaScraperItem()
        item["title"] = self.manga_title
        item["chapter"] = url_segments[len(url_segments) - 1]
        item["pages"] = {
            img_num.strip(): img_src.strip()
            for img_num, img_src in zip(img_nums, img_srcs)
        }

        yield item


class RotlSpider(BaseSpider):
    name = "rotl"
    start_urls = ["https://mangajar.com/manga/ruler-of-the-land-abs3VDC"]
    manga_title = "ruler-of-the-land"


class AodIISpider(BaseSpider):
    name = "aod2"
    start_urls = ["https://mangajar.com/manga/diamond-no-ace-act-ii-abs3Top"]
    manga_title = "ace-of-diamond-2"


class KnyaSpider(BaseSpider):
    name = "knya"
    start_urls = ["https://mangajar.com/manga/kimetsu-no-yaiba"]
    manga_title = "kinematsu-no-yaiba"
