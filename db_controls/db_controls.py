from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models.home import Home
from models.link import Link
from sqlalchemy.orm import sessionmaker
import logging

engine = None
Session = sessionmaker()


class Home_db_control():
    def __init__(self, database):
        self.logger = logging.getLogger("Home_db_control")
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
            self.logger.error(e)
            self.close_engine()

    def add_unit(self, home_):
        try:
            rows = self.select_units(mls = home_.mls)
            if len(rows) != 0:
                self.logger.info("record is alread there. skipping adding...")
                return
            self.logger.info("adding home on mls {}".format(home_.mls))
            self.session.add(home_)
            self.session.commit()
            self.logger.info("successfully added.")
        except SQLAlchemyError as e:
            self.logger.error(e)
            self.close_engine()

    def add_units(self, *homes):
        errormls = str()
        try:
            for hm in homes[0]:
                self.logger.info("adding home on mls {}".format(hm.mls))
                errormls = hm.mls
                self.session.add(hm)
            self.session.commit()
            self.logger.info("successfully added {} homes.".format(len(homes)))
        except SQLAlchemyError as e:
            self.logger.error("error in adding home (#{}). {}".format(errormls, str(e)))
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
            self.close_engine()

    def close_engine(self):
        global engine
        try:
            self.session.bind.dispose()
            engine.dispose()
        except Exception as e:
            self.logger.error("Unknown error while closing database related. {}".format(str(e)))


class Link_db_control():
    def __init__(self, database):
        self.logger = logging.getLogger("Link_db_control")
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
                rows = self.session.query(Link).filter(getattr(Link, attr) == value).all()
            return rows
        except SQLAlchemyError as e:
            self.logger.error(e)
            self.close_engine()

    def add_links(self, *links):
        already_in = []
        try:
            for l in links[0]:
                found = self.select_links(link = l)
                if found is not None and len(found) == 0:
                    self.session.add(Link(l))
                else:
                    already_in.append(l)
            self.session.commit()
            self.logger.info("Total link amount is {}. {} links are already in the database:".format(len(links[0]), len(already_in)))
            self.logger.info(already_in)
        except SQLAlchemyError as e:
            self.logger.error("error in adding link {}. {}".format(l, str(e)))
            self.close_engine()

    def close_engine(self):
        global engine
        try:
            self.session.bind.dispose()
            engine.dispose()
        except Exception as e:
            self.logger.error("Unknown error while closing database related. {}".format(str(e)))