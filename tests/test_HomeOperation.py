import unittest
from operations.home_operation import HomeOperation


class TestHomeOperation(unittest.TestCase):
    def test_fetch_basic_info_1(self):
        url = "https://www.redfin.com/WA/Vashon/80-SW-Hawthorne-Ln-98070/home/145985726"
        keys = [
            "address", "city", "state", "zipcode", "status", "price", "beds",
            "bath", "sqft", "lot_size", "on_redfin", "property_type", "style",
            "views", "community", "county", "mls"
        ]
        self.__call_fetch_data_func(url, keys)

    def test_fetch_basic_info_2(self):
        url = "https://www.redfin.com/WA/Bothell/20056-94th-Dr-NE-98011/unit-8/home/59704159"
        keys = [
            "address", "city", "state", "zipcode", "status", "price", "beds",
            "bath", "sqft", "per_sqft", "built", "lot_size", "on_redfin",
            "hoa_dues", "property_type", "style", "views", "community",
            "county", "mls"
        ]
        self.__call_fetch_data_func(url, keys)

    def test_fetch_basic_info_3(self):
        url = "https://www.redfin.com/WA/Bothell/20021-95th-Pl-NE-98011/home/286382"
        keys = [
            "address", "city", "state", "zipcode", "status", "redfin_estimate",
            "last_sold_price", "beds", "bath", "sqft", "per_sqft", "built",
            "lot_size", "property_type", "style", "community", "county", "mls"
        ]
        self.__call_fetch_data_func(url, keys)

    def test_fetch_basic_info_4(self):
        url = "https://www.redfin.com/WA/Tacoma/Autumn-Grove/AG-3517B/home/144415476"
        keys = [
            "address", "city", "state", "zipcode", "status", "price", "beds",
            "bath", "sqft", "per_sqft", "ommunity", "county", "listing"
        ]
        self.__call_fetch_data_func(url, keys)

    def test_fetch_basic_info_5(self):
        url = "https://www.redfin.com/WA/Seattle/156-15th-Ave-98122/unit-A/home/145445"
        keys = [
            "address", "city", "state", "zipcode", "status", "listed_at_price",
            "redfin_estimate", "beds", "bath", "sqft", "per_sqft", "on_redfin",
            "built", "lot_size", "property_type", "style", "community",
            "county", "mls", "views", "offer_review_date"
        ]
        self.__call_fetch_data_func(url, keys)

    def __call_fetch_data_func(self, url, keys):
        ho = HomeOperation(url)
        ho.fetch_data()
        print(ho.info.keys())
        print(keys)
        not_in = [key for key in keys if key not in ho.info.keys()]
        self.assertTrue(len(not_in) == 0, ", ".join(not_in))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHomeOperation)
    unittest.TextTestRunner(verbosity=2).run(suite)