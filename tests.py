import unittest

from app.models import Publisher


class PublisherTest(unittest.TestCase):
    def setUp(self):
        self.publisher_1 = Publisher(
            name="Jude Southworth",
            email="judesouthworth@pm.me",
        )
        self.publisher_2 = Publisher(
            name="Orr Bezalely",
            email="orr.bezalely@pm.me",
        )

    def test_publisher_set_passwords(self):
        self.assertTrue(self.publisher_1.password_hash is None)
        self.assertTrue(self.publisher_2.password_hash is None)

        self.publisher_1.password = "jude1234"
        self.publisher_2.password = "orr1234"

        self.assertFalse(self.publisher_1.password_hash is None)
        self.assertFalse(self.publisher_2.password_hash is None)

    def test_publisher_check_passwords(self):
        self.publisher_1.password = "jude1234"
        self.publisher_2.password = "orr1234"

        self.assertTrue(self.publisher_1.check_password("jude1234"))
        self.assertTrue(self.publisher_2.check_password("orr1234"))
        self.assertFalse(self.publisher_1.check_password("klsijlkajsd"))
        self.assertFalse(self.publisher_2.check_password("lkasjdlkajsf"))


if __name__ == "__main__":
    unittest.main()
