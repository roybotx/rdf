from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
import datetime

base = declarative_base()


class Link(base):
    __tablename__ = "links"
    id = Column(Integer, primary_key = True, autoincrement = True)
    link = Column(String(500), nullable = False)
    crawled = Column(Integer, default = 0)
    home_type = Column(Integer, default = 0)
    creation_date = Column(Date, default = datetime.datetime.now())
    modification_date = Column(Date, default = datetime.datetime.now())

    def __init__(self, link_, home_type_, crawled_ = 0, creation_date_ = datetime.datetime.now(), mod_date_ = datetime.datetime.now()):
        self.link = link_
        self.crawled = crawled_
        self.creation_date = creation_date_
        self.modification_date = mod_date_
        self.home_type = home_type_
