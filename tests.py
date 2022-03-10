import re
import unittest

from app import create_app, db
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
        self.assertIsNone(self.publisher_1.password_hash)
        self.assertIsNone(self.publisher_2.password_hash)

        self.publisher_1.password = "jude1234"
        self.publisher_2.password = "orr1234"

        self.assertIsNotNone(self.publisher_1.password_hash)
        self.assertIsNotNone(self.publisher_2.password_hash)

    def test_publisher_check_passwords(self):
        self.publisher_1.password = "jude1234"
        self.publisher_2.password = "orr1234"

        self.assertTrue(self.publisher_1.check_password("jude1234"))
        self.assertTrue(self.publisher_2.check_password("orr1234"))

        self.assertFalse(self.publisher_1.check_password("klsijlkajsd"))
        self.assertFalse(self.publisher_2.check_password("lkasjdlkajsf"))


class RouteTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.publisher_1 = Publisher(
            name="Jude Southworth",
            email="judesouthworth@pm.me",
        )

        db.session.add(self.publisher_1)
        db.session.commit()

        self.publisher_2 = Publisher(
            name="Orr Bezalely",
            email="orr.bezalely@pm.me",
        )

        db.session.add(self.publisher_2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_publisher_400(self):
        req1 = self.client.get("/api/v1/publisher")
        req2 = self.client.get("/api/v1/publisher", json={})

        self.assertEqual(req1.status_code, 400)
        self.assertEqual(req2.status_code, 400)

    def test_get_publisher_404(self):
        req1 = self.client.get("/api/v1/publisher", json={"id": 3})
        req2 = self.client.get("/api/v1/publisher", json={"id": "a"})

        self.assertEqual(req1.status_code, 404)
        self.assertEqual(req2.status_code, 404)

    def test_get_publisher(self):
        req1 = self.client.get("/api/v1/publisher", json={"id": self.publisher_1.id})
        req2 = self.client.get("/api/v1/publisher", json={"id": self.publisher_2.id})

        self.assertEqual(req1.status_code, 200)
        self.assertEqual(req2.status_code, 200)

        self.assertEqual(req1.json["name"], self.publisher_1.name)
        self.assertEqual(req1.json["email"], self.publisher_1.email)

        self.assertEqual(req2.json["name"], self.publisher_2.name)
        self.assertEqual(req2.json["email"], self.publisher_2.email)

    def test_create_publisher_409(self):
        req1 = self.client.put(
            "/api/v1/publisher",
            json={"name": self.publisher_1.name, "email": self.publisher_1.email},
        )

        self.assertEqual(req1.status_code, 409)

    def test_create_publisher_400(self):
        req1 = self.client.put(
            "/api/v1/publisher", json={"name": "Jude", "email": "invalid"}
        )
        req2 = self.client.put(
            "/api/v1/publisher", json={"name": "Jude", "email": "invalid@also"}
        )
        req3 = self.client.put(
            "/api/v1/publisher", json={"name": "Jude", "email": "invalid.also"}
        )
        req4 = self.client.put(
            "/api/v1/publisher", json={"name": "Jude", "email": "invalid@also. "}
        )

        self.assertEqual(req1.status_code, 400)
        self.assertEqual(req2.status_code, 400)
        self.assertEqual(req3.status_code, 400)
        self.assertEqual(req4.status_code, 400)

    def test_create_publisher(self):
        # put new publisher to API
        req1 = self.client.put(
            "/api/v1/publisher", json={"name": "Taliesin Oldridge", "email": "to@pm.me"}
        )

        self.assertEqual(req1.status_code, 200)
        self.assertEqual(req1.json["name"], "Taliesin Oldridge")
        self.assertEqual(req1.json["email"], "to@pm.me")
        self.assertIsNotNone(re.match(r"^\S{16}$", req1.json["password"]))

        # retrieve the publisher back from the API
        req2 = self.client.get(
            "/api/v1/publisher", json={"id": self.publisher_2.id + 1}
        )

        self.assertEqual(req2.status_code, 200)
        self.assertEqual(req2.json["name"], "Taliesin Oldridge")
        self.assertEqual(req2.json["email"], "to@pm.me")


if __name__ == "__main__":
    unittest.main()
