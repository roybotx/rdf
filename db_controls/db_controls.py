from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models.home import Home
from sqlalchemy.orm import sessionmaker

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
            print(e)

    def add_unit(self, home_):
        try:
            rows = self.select_units(mls = home_.mls)
            if len(rows) != 0:
                print("record is alread there. skipping adding...")
                return
            print("adding home on mls {}".format(home_.mls))
            self.session.add(home_)
            self.session.commit()
            print("successfully added.")
        except SQLAlchemyError as e:
            print(e)

    def add_units(self, *homes):
        errormls = str()
        try:
            for hm in homes:
                print("adding home on mls {}".format(hm.mls))
                errormls = hm.mls
                self.session.add(hm)
            self.session.commit()
            print("successfully added {} homes.".format(len(homes)))
        except SQLAlchemyError as e:
            print("error in adding home (#{}). {}".format(errormls, str(e)))

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
            print(e)

    def delete_unit_on_mls(self, mls):
        try:
            row = self.session.query(Home).filter(Home.mls == mls)
            print("going to delete %s" % row)
            row.delete()
            self.session.commit()
            print("successfully deleted.")
        except SQLAlchemyError as e:
            print(e)

    def close_engine(self):
        global engine
        self.session.bind.dispose()
        self.session.dispose()
        engine.dispose()
