import sqlite3


class DbTracker:
    t_manga_crt_qry = """
        CREATE TABLE IF NOT EXISTS MANGA (
            manga_spider TEXT NOT NULL,
            chapter TEXT NOT NULL,
            page TEXT NOT NULL,
            url TEXT NOT NULL,
            path TEXT, 
            UNIQUE(chapter, page)
        );
    """

    t_manga_drp_qry = """
        DROP TABLE IF EXISTS MANGA
    """

    t_manga_insert = """
        INSERT INTO MANGA VALUES(?, ?, ?, ?, ?)
    """

    t_manga_select_all = """
        SELECT * FROM MANGA
    """

    t_manga_search = """
        SELECT * FROM MANGA
        WHERE manga_spider = ?
        AND chapter = ?
        AND page = ?
    """

    def __init__(self, fpath_db: str, spider_name: str):
        self.con = sqlite3.connect(fpath_db)
        self.cur = self.con.cursor()
        self.spider_name = spider_name

    def __exit__(self, *args):
        self.con.close()

    def create(self):
        self.cur.execute(self.t_manga_crt_qry)

    def drop(self):
        self.cur.execute(self.t_manga_drp_qry)

    def insert(self, chapter: str, page: str, url: str, path: str):
        self.cur.execute(
            self.t_manga_insert, (self.spider_name, chapter, page, url, path)
        )
        self.con.commit()

    def insertmany(self, ldata: list):
        self.cur.executemany(self.t_manga_insert, ldata)
        self.con.commit()

    def search(self, chapter: str, page: str) -> list:
        self.cur.execute(self.t_manga_search, (self.spider_name, chapter, page))
        return self.cur.fetchall()
