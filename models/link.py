from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class Link(base):
    __tablename__ = "links"
    id = Column(Integer, primary_key = True, autoincrement = True)
    link = Column(String(500), nullable = False)
    crawled = Column(Integer, default = 0)

    def __init__(self, link_, crawled_ = 0):
        self.link = link_
        self.crawled = crawled_
