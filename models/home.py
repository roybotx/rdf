from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
import datetime

base = declarative_base()


class Home(base):
    __tablename__ = "homes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Float)
    lot_size = Column(Float)
    status = Column(String(10))
    built = Column(String)
    address = Column(String(200))
    redfin_estimate = Column(Float)
    last_sold_price = Column(Float)
    beds = Column(Integer)
    bath = Column(Float)
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
    listed_at_price = Column(Float)
    on_redfin = Column(Integer)
    city = Column(String)
    creation_date = Column(Date, default=datetime.datetime.now())
    modification_date = Column(Date, default=datetime.datetime.now())

    def __repr__(self):
        return "id:{}, price:{}, lot_size:{}, status:{}, built:{}, address:{}, redfin_estimate:{}, last_sold_price:{}, beds:{}, bath:{}, sqft:{}, per_sqft:{}, hoa_dues:{}, property_type:{}, style:{}, floor_number:{}, stories:{}, views:{}, offer_review_date:{}, community:{}, county:{}, mls:{}, zipcode:{}, state:{}, link:{}, listed_at_price:{}, on_redfin:{}, city:{}, creation_date:{}, modification_date:{}".format(
            self.id, self.price, self.lot_size, self.status, self.built,
            self.address, self.redfin_estimate, self.last_sold_price,
            self.beds, self.bath, self.sqft, self.per_sqft, self.hoa_dues,
            self.property_type, self.style, self.floor_number, self.stories,
            self.views, self.offer_review_date, self.community, self.county,
            self.mls, self.zipcode, self.state, self.link,
            self.listed_at_price, self.on_redfin, self.city,
            self.creation_date, self.modification_date)

    valid_keys = [
        "price", "lot_size", "status", "built", "address", "redfin_estimate",
        "last_sold_price", "beds", "bath", "sqft", "per_sqft", "hoa_dues",
        "property_type", "style", "floor_number", "stories", "views",
        "offer_review_date", "community", "county", "mls", "zipcode", "state",
        "link", "on_redfin", "listed_at_price", "city"
    ]

    def __init__(self,
                 dic,
                 creation_date_=datetime.datetime.now(),
                 modification_date_=datetime.datetime.now()):
        for key in self.valid_keys:
            self.__dict__[key] = dic.get(key)
        self.creation_date = creation_date_
        self.modification_date = modification_date_
