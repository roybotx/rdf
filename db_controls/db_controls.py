from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models.home import Home
from sqlalchemy.orm import sessionmaker
import logging
from sqlalchemy.exc import OperationalError, DataError

engine = None
Session = sessionmaker()


class HomeDBControl():
    def __init__(self):
        self.logger = logging.getLogger("HomeDBControl")
        db_url = {
            "database": "housing",
            "drivername": "mysql",
            "username": "root",
            "password": "",
            "host": "localhost",
            "port": 3306
        }
        global engine
        engine = create_engine(URL(**db_url), encoding = "utf8")
        Session.configure(bind=engine)
        self.session = Session()

    def select_units(self, **kwargs):
        try:
            for attr, value in kwargs.items():
                rows = self.session.query(Home).filter(getattr(Home, attr) == value).all()
            return rows
        except SQLAlchemyError as e:
            self.logger.error(e)
            self.session.rollback()
            self.close_engine()

    def add_unit(self, home_):
        try:
            rows = self.select_units(link = home_.link)
            if len(rows) != 0:
                self.logger.info("record is alread there. skipping adding...")
                return
            self.logger.info("adding {}, {}, {} {}".format(home_.address, home_.city, home_.state, home_.zipcode))
            self.logger.info("=" * 23 + "dict" + "=" * 23)
            self.logger.info(home_.__repr__())
            self.logger.info("=" * 50)
            self.session.add(home_)
            self.session.commit()
            self.logger.info("successfully added.")
        except (OperationalError, DataError) as e:
            self.logger.error(e)
            self.session.rollback()
            self.session.add(Home({"link": home_.link}, False))
            self.session.commit()
        except Exception as e:
            self.logger.error(e)
            self.session.rollback()
            self.close_engine()

    def add_units(self, *homes):
        try:
            for hm in homes[0]:
                address = "{}, {}, {} {}".format(hm.address, hm.city, hm.state, hm.zipcode)
                self.logger.info("adding {}".format(address))
                self.logger.info("=" * 23 + "dict" + "=" * 23)
                self.logger.info(hm.__repr__())
                self.logger.info("=" * 50)
                self.session.add(hm)
            self.session.commit()
            self.logger.info("successfully added {} homes.".format(len(homes[0])))
        except SQLAlchemyError as e:
            self.logger.error("error in adding home ({}). {}".format(address, str(e)))
            self.session.rollback()
            self.close_engine()

    def update_unit_on_mls(self, mls, **values):
        try:
            row = self.session.query(Home).filter(Home.mls == mls).first()
            for key, value in values:
                if key in Home.valid_keys:
                    row[key] = value
                else:
                    pass
            self.session.commit()
        except SQLAlchemyError as e:
            self.logger.error(e)
            self.session.rollback()
            self.close_engine()

    def delete_unit_on_mls(self, mls):
        try:
            row = self.session.query(Home).filter(Home.mls == mls)
            self.logger.info("going to delete %s" % row)
            row.delete()
            self.session.commit()
            self.logger.info("successfully deleted.")
        except SQLAlchemyError as e:
            self.logger.error(e)
            self.session.rollback()
            self.close_engine()

    def close_engine(self):
        global engine
        try:
            self.session.bind.dispose()
            engine.dispose()
        except Exception as e:
            self.logger.error("Unknown error while closing database related. {}".format(str(e)))
