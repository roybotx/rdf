from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models.home import Home
from models.link import Link
from sqlalchemy.orm import sessionmaker
from my_logger import logger

engine = None
Session = sessionmaker()


class Home_db_control():
    def __init__(self, database):
        db_url = {
            "database": database,
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
            logger.error(e)

    def add_unit(self, home_):
        try:
            rows = self.select_units(mls = home_.mls)
            if len(rows) != 0:
                logger.info("record is alread there. skipping adding...")
                return
            logger.info("adding home on mls {}".format(home_.mls))
            self.session.add(home_)
            self.session.commit()
            logger.info("successfully added.")
        except SQLAlchemyError as e:
            logger.error(e)

    def add_units(self, *homes):
        errormls = str()
        try:
            for hm in homes[0]:
                logger.info("adding home on mls {}".format(hm.mls))
                errormls = hm.mls
                self.session.add(hm)
            self.session.commit()
            logger.info("successfully added {} homes.".format(len(homes)))
        except SQLAlchemyError as e:
            logger.error("error in adding home (#{}). {}".format(errormls, str(e)))

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
            logger.error(e)

    def delete_unit_on_mls(self, mls):
        try:
            row = self.session.query(Home).filter(Home.mls == mls)
            logger.info("going to delete %s" % row)
            row.delete()
            self.session.commit()
            logger.info("successfully deleted.")
        except SQLAlchemyError as e:
            logger.error(e)

    def close_engine(self):
        global engine
        try:
            self.session.bind.dispose()
            engine.dispose()
        except Exception as e:
            logger.error("Unknown error while closing database related. {}".format(str(e)))


class Link_db_control():
    def __init__(self, database):
        db_url = {
            "database": database,
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

    def select_links(self, **kwargs):
        try:
            for attr, value in kwargs.items():
                rows = self.session.query(Link).filter(getattr(Home, attr) == value).all()
            return rows
        except SQLAlchemyError as e:
            logger.error(e)

    def add_links(self, *links):
        try:
            for l in links[0]:
                found = self.select_links(link = l)
                if found is not None and found == 0:
                    self.session.add(l)
                else:
                    logger.info("{} is already in the database.".format(l))
            self.session.commit()
        except SQLAlchemyError as e:
            logger.error("error in adding link {}. {}".format(l, str(e)))

    def close_engine(self):
        global engine
        try:
            self.session.bind.dispose()
            engine.dispose()
        except Exception as e:
            logger.error("Unknown error while closing database related. {}".format(str(e)))