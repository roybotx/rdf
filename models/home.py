from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base


base = declarative_base()
metadata = base.metadata


class Home(base):
    __tablename__ = "homes"
    id = Column(Integer, primary_key=True)
    stats = Column(String(10))
    built = Column(Integer)
    address = Column(String(200))
    redfin_estimate = Column(Float)
    last_sold_price = Column(Float)
    beds = Column(Integer)
    bath = Column(Integer)
    sqft = Column(Integer)
    per_sqft = Column(Float)
    hoa_dues = Column(Float)
    property_type = Column(String(20))
    style = Column(String(10))
    floor_number = Column(Integer)
    stories = Column(Integer)
    views = Column(String(20))
    offer_review_date = Column(Date)
    community = Column(String(20))
    county = Column(String(10))
    mls = Column(Integer)
    zipcode = Column(String(5))
    state = Column(String(4))
    link = Column(String(500), nullable=False)
    valid_keys = [
        "stats", "built", "address", "redfin_estimate",
        "last_sold_price", "beds", "bath", "sqft", "per_sqft", "hoa_dues",
        "property_type", "style", "floor_number", "stories", "views",
        "offer_review_date", "community", "county", "mls", "zipcode",
        "state", "link"
    ]

    def __init__(self, dic):
        for key in self.valid_keys:
            self.__dict__[key] = dic.get(key)