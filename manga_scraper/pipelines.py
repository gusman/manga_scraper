# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import requests
import time

from PIL import Image
from io import BytesIO
from pathlib import Path
from scrapy.pipelines.images import ImageException

from manga_scraper.db_tracker import DbTracker 

class MangaImagePipeline:
    img_min_h = 24 
    img_min_w = 24 

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_path = crawler.settings.get('SQLITE3_PATH'),
            spider_name = crawler.spider.name,
            manga_title = crawler.spider.manga_title,
            manga_dir = crawler.settings.get('MANGA_DIR'),
            img_dwnld_delay = crawler.settings.get('IMG_DOWNLOAD_DELAY'),
        )

    def __init__(self, db_path, spider_name, manga_title, manga_dir, img_dwnld_delay):
        self.db_tracker = DbTracker(db_path, spider_name)
        self.db_tracker.create()
        self.manga_dir = manga_dir + '/' + manga_title
        self.img_dwnld_delay = img_dwnld_delay

    def process_item(self, item, spider):
        chapter = item['chapter']
        chapter_dir = self.manga_dir + '/' + str(chapter).zfill(4)
        Path(chapter_dir, exits_ok = True).mkdir(parents=True, exist_ok=True)

        pages = item['pages']
        for page, url in pages.items():
           
            """ Download the image """
            result = self.db_tracker.search(chapter, page)
            if 0 >= len(result):
                page_num = str(page).zfill(2)
                page_path = chapter_dir + '/' + page_num 

                page_path = self.download_image(url, page_path)

                if page_path is not None:
                    self.db_tracker.insert(chapter, page, url, page_path)
                    time.sleep(self.img_dwnld_delay)
                else:
                    raise ImageException(f'Image for {chapter} and {page} is too small')
        
        return item

    def download_image(self, url, page_path):
        retval = None
        img_req = requests.get(url)
        img_pic = Image.open(BytesIO(img_req.content))
        img_w, img_h =  img_pic.size 

        if (img_w >= self.img_min_w and img_h >= self.img_min_h):
            page_path = page_path + '.' + img_pic.format
            img_pic.save(page_path)
            retval = page_path

        return retval
