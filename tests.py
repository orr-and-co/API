import re
import time
import unittest
from base64 import b64encode
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Post, Publisher


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


class PublisherRouteTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.publisher_1 = Publisher(
            name="Jude Southworth", email="judesouthworth@pm.me", full_admin=True
        )
        self.publisher_2 = Publisher(
            name="Orr Bezalely",
            email="orr.bezalely@pm.me",
        )

        db.session.add(self.publisher_1)
        db.session.add(self.publisher_2)
        db.session.commit()

        self.headers = {
            "Authorization": "Basic {}".format(
                b64encode(
                    "{}:".format(self.publisher_1.generate_auth_token(120)).encode(
                        "utf-8"
                    )
                ).decode("utf-8")
            )
        }

        self.headers_orr = {
            "Authorization": "Basic {}".format(
                b64encode(
                    "{}:".format(self.publisher_2.generate_auth_token(120)).encode(
                        "utf-8"
                    )
                ).decode("utf-8")
            )
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_authorization(self):
        req1 = self.client.get("/api/v1/publisher/1/")
        req2 = self.client.put(
            "/api/v1/publisher/",
            json={"name": "Taliesin Oldridge", "email": "to@pm.me"},
        )

        self.assertEqual(req1.status_code, 401)
        self.assertEqual(req2.status_code, 401)

    def test_get_publisher_404(self):
        req1 = self.client.get("/api/v1/publisher/3/", headers=self.headers)
        req2 = self.client.get("/api/v1/publisher/a/", headers=self.headers)

        self.assertEqual(req1.status_code, 404)
        self.assertEqual(req2.status_code, 404)

    def test_get_publisher(self):
        req1 = self.client.get(
            "/api/v1/publisher/{}/".format(self.publisher_1.id), headers=self.headers
        )
        req2 = self.client.get(
            "/api/v1/publisher/{}/".format(self.publisher_2.id), headers=self.headers
        )

        self.assertEqual(req1.status_code, 200)
        self.assertEqual(req2.status_code, 200)

        self.assertEqual(req1.json["name"], self.publisher_1.name)
        self.assertEqual(req1.json["email"], self.publisher_1.email)

        self.assertEqual(req2.json["name"], self.publisher_2.name)
        self.assertEqual(req2.json["email"], self.publisher_2.email)

    def test_create_publisher_403(self):
        req1 = self.client.put(
            "/api/v1/publisher/",
            json={"name": "Taliesin Oldridge", "email": "to@pm.me"},
            headers=self.headers_orr,
        )

        self.assertEqual(req1.status_code, 403)

    def test_create_publisher_409(self):
        req1 = self.client.put(
            "/api/v1/publisher/",
            json={"name": self.publisher_1.name, "email": self.publisher_1.email},
            headers=self.headers,
        )

        self.assertEqual(req1.status_code, 409)

    def test_create_publisher_400(self):
        req1 = self.client.put(
            "/api/v1/publisher/",
            json={"name": "Jude", "email": "invalid"},
            headers=self.headers,
        )
        req2 = self.client.put(
            "/api/v1/publisher/",
            json={"name": "Jude", "email": "invalid@also"},
            headers=self.headers,
        )
        req3 = self.client.put(
            "/api/v1/publisher/",
            json={"name": "Jude", "email": "invalid.also"},
            headers=self.headers,
        )
        req4 = self.client.put(
            "/api/v1/publisher/",
            json={"name": "Jude", "email": "invalid@also. "},
            headers=self.headers,
        )

        self.assertEqual(req1.status_code, 400)
        self.assertEqual(req2.status_code, 400)
        self.assertEqual(req3.status_code, 400)
        self.assertEqual(req4.status_code, 400)

    def test_create_publisher(self):
        # put new publisher to API
        req1 = self.client.put(
            "/api/v1/publisher/",
            json={"name": "Taliesin Oldridge", "email": "to@pm.me"},
            headers=self.headers,
        )

        self.assertEqual(req1.status_code, 200)
        self.assertEqual(req1.json["name"], "Taliesin Oldridge")
        self.assertEqual(req1.json["email"], "to@pm.me")
        self.assertIsNotNone(re.match(r"^\S{16}$", req1.json["password"]))

        # retrieve the publisher back from the API
        req2 = self.client.get(
            "/api/v1/publisher/{}/".format(self.publisher_2.id + 1),
            headers=self.headers,
        )

        self.assertEqual(req2.status_code, 200)
        self.assertEqual(req2.json["name"], "Taliesin Oldridge")
        self.assertEqual(req2.json["email"], "to@pm.me")

    def test_update_publisher(self):
        req1 = self.client.patch(
            "/api/v1/publisher/", json={"email": "js@pm.me"}, headers=self.headers
        )

        self.assertEqual(req1.status_code, 201)

        req2 = self.client.get(
            "/api/v1/publisher/{}/".format(self.publisher_1.id), headers=self.headers
        )

        self.assertEqual(req2.json["email"], "js@pm.me")

        previous_hash = self.publisher_1.password_hash
        req3 = self.client.patch(
            "/api/v1/publisher/", json={"password": "1234"}, headers=self.headers
        )

        self.assertEqual(req3.status_code, 201)
        self.assertNotEqual(self.publisher_1.password_hash, previous_hash)


class PostRouteTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.publisher_1 = Publisher(
            name="Tyler Durden",
            email="narrator@pm.me",
        )

        db.session.add(self.publisher_1)
        db.session.flush()

        self.posts = [
            Post(
                title=title,
                content=title,
                published_at=datetime.fromisoformat(date),
                publisher=self.publisher_1,
            )
            for title, date in zip(
                ["1", "2", "3", "4", "5", "6"],
                [
                    "2022-03-05",
                    "2022-03-10",
                    "2022-03-03",
                    "2022-03-04",
                    "2022-03-07",
                    "2022-03-02",
                ],
            )
        ]

        [db.session.add(post) for post in self.posts]

        for i in range(7, 35):
            post = Post(
                title=str(i),
                content=str(i),
                published_at=datetime.fromisoformat("2022-03-02") - timedelta(days=i),
            )
            db.session.add(post)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_recent_posts(self):
        req = self.client.get("/api/v1/posts/recent/")

        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json[0]["title"], "2")
        self.assertEqual(req.json[1]["title"], "5")
        self.assertEqual(req.json[2]["title"], "1")
        self.assertEqual(req.json[3]["title"], "4")
        self.assertEqual(req.json[4]["title"], "3")
        self.assertEqual(req.json[5]["title"], "6")

        for i in range(6, 15):
            self.assertEqual(req.json[i]["title"], str(i + 1))

    def test_posts_page(self):
        req1 = self.client.get("/api/v1/posts/recent/?page=2")
        req2 = self.client.get("/api/v1/posts/recent/?page=3")
        req3 = self.client.get("/api/v1/posts/recent/?page=4")

        self.assertEqual(req1.status_code, 200)
        self.assertEqual(req2.status_code, 200)
        self.assertEqual(req3.status_code, 404)

        for i in range(0, 15):
            self.assertEqual(req1.json[i]["title"], str(i + 16))

        for count, post in enumerate(req2.json, start=31):
            self.assertEqual(post["title"], str(count))

    def test_get_post(self):
        req1 = self.client.get("/api/v1/posts/1/")

        self.assertEqual(req1.status_code, 200)
        self.assertEqual(req1.json["title"], "1")
        self.assertEqual(req1.json["publisher"]["name"], "Tyler Durden")

        req2 = self.client.get("/api/v1/posts/100/")

        self.assertEqual(req2.status_code, 404)


class PostRouteTest2(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.publisher = Publisher()
        db.session.add(self.publisher)
        db.session.commit()

        self.headers = {
            "Authorization": "Basic {}".format(
                b64encode(
                    "{}:".format(self.publisher.generate_auth_token(120)).encode(
                        "utf-8"
                    )
                ).decode("utf-8")
            )
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_authorization(self):
        req1 = self.client.post("/api/v1/posts/")

        self.assertEqual(req1.status_code, 401)

    def test_create_post_400(self):
        req1 = self.client.post(
            "/api/v1/posts/",
            headers=self.headers,
        )
        req2 = self.client.post("/api/v1/posts/", json={}, headers=self.headers)
        req3 = self.client.post(
            "/api/v1/posts/", json={"title": "abc"}, headers=self.headers
        )
        req4 = self.client.post(
            "/api/v1/posts/", json={"content": "abc"}, headers=self.headers
        )
        req5 = self.client.post(
            "/api/v1/posts/",
            json={"content": "abc", "link": "abc"},
            headers=self.headers,
        )
        req6 = self.client.post(
            "/api/v1/posts/",
            json={"content": "abc", "link": "abc"},
            headers=self.headers,
        )
        req7 = self.client.post(
            "/api/v1/posts/", json={"link": "abc"}, headers=self.headers
        )

        self.assertEqual(req1.status_code, 400)
        self.assertEqual(req2.status_code, 400)
        self.assertEqual(req3.status_code, 400)
        self.assertEqual(req4.status_code, 400)
        self.assertEqual(req5.status_code, 400)
        self.assertEqual(req6.status_code, 400)
        self.assertEqual(req7.status_code, 400)

    def test_create_post_now(self):
        req1 = self.client.post(
            "/api/v1/posts/",
            json={
                "title": "id like to interject for a moment",
                "content": "What you are refering to as Linux is in fact GNU/Linux, or as I have begun saying, GNU slash Linux.",
                "publish_at": time.time() - 1,
            },
            headers=self.headers,
        )

        self.assertEqual(req1.status_code, 200)

        req2 = self.client.get("/api/v1/posts/{}/".format(req1.json["id"]))
        req3 = self.client.get("/api/v1/posts/recent/")

        self.assertEqual(req2.status_code, 200)
        self.assertEqual(len(req3.json), 1)
        self.assertEqual(req2.json["title"], "id like to interject for a moment")
        self.assertEqual(
            req3.json[0]["content"],
            "What you are refering to as Linux is in fact GNU/Linux, or as I have begun saying, GNU slash Linux.",
        )

    def test_create_post_future(self):
        req1 = self.client.post(
            "/api/v1/posts/",
            json={
                "title": "id like to interject for a moment",
                "content": "What you are refering to as Linux is in fact GNU/Linux, or as I have begun saying, GNU slash Linux.",
            },
            headers=self.headers,
        )

        self.assertEqual(req1.status_code, 200)

        req2 = self.client.get("/api/v1/posts/{}/".format(req1.json["id"]))
        req3 = self.client.get("/api/v1/posts/recent/")

        self.assertEqual(req2.status_code, 404)
        self.assertEqual(req3.json, [])


if __name__ == "__main__":
    unittest.main()
