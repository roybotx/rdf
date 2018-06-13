from sqlalchemy import (Column, Integer, String)
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class Link(base):
    __tablename__ = "links"
    id = Column(Integer, primary_key = True)
    link = Column(String, nullable = False)

    def __init__(self, link_):
        self.link = link_
