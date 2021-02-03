from django.test import TestCase
import os
from .InstagramScraper import InstagramScraper


class InstagramScraperTests(TestCase):
    PROFILE = "mihaianton98"
    MINIMUM_EXPECTED_POSTS = 5
    SINGLE_IMAGE_POST = "/p/Bm89h2KnvJc/"
    EXPECTED_IMAGE_URL = "https://instagram.fclj2-1.fna.fbcdn.net/v/t51.2885-15/e35/39225876_" +\
        "678669832491548_8313827882027712512_n.jpg?_nc_ht=instagram.fclj2-1.fna.fbcdn.net&_nc_cat=108&_" +\
        "nc_ohc=nALU87zGuxkAX_4tD5n&tp=1&oh=80f472a8e913ddba12ee8d002d986cb9&oe=6043B22F"
    POST_PATH = "https://www.instagram.com/p/Bm89h2KnvJc/"
    EXPECTED_DESCRIPTION = "Adventure time ⛰"

    MULTIPLE_IMAGE_POST = "/p/CDYaJpfDPT0/"
    EXPECTED_IMAGE_COUNT = 4
    EXPECTED_IMAGE_URL_2 = "https://instagram.fclj2-1.fna.fbcdn.net/v/t51.2885-15/e35/s1080x1080/116227506" +\
        "_3495454757146010_540113168384077450_n.jpg?_nc_ht=instagram.fclj2-1.fna.fbcdn.net&_nc_cat=102&_nc_" +\
        "ohc=rhsuW61DgF8AX_eMw51&tp=1&oh=8e888f8c066de6ef8a8427d30599eb0b&oe=604451EE"

    def setUp(self):
        self._user = os.environ.get("INSTAGRAM_USERNAME")
        self._pass = os.environ.get("INSTAGRAM_PASSWORD")
        self._scraper = InstagramScraper(self._user, self._pass)

    def test_environ_variables(self):
        self.assertIsNotNone(self._user)
        self.assertIsNotNone(self._pass)

    def test_scrape_post_single_image(self):
        data = self._scraper.scrape_post(self.SINGLE_IMAGE_POST)

        self.assertEqual(data.get("description", ""), self.EXPECTED_DESCRIPTION)
        self.assertEqual(len(data.get("photo_urls", [])), 1)
        self.assertEqual(data.get("photo_urls", [])[0], self.EXPECTED_IMAGE_URL)

    def test_scrape_post_multiple_images(self):
        data = self._scraper.scrape_post(self.MULTIPLE_IMAGE_POST)

        self.assertEqual(len(data.get("photo_urls", [])), self.EXPECTED_IMAGE_COUNT)
        self.assertTrue(self.EXPECTED_IMAGE_URL_2 in data.get("photo_urls", []))

    def test_scrape_profile(self):
        info = self._scraper.scrape_profile(self.PROFILE)

        self.assertTrue("posts" in info)
        posts = info["posts"]

        self.assertGreaterEqual(len(posts), self.MINIMUM_EXPECTED_POSTS)
        self.assertTrue(any(post["path"] == self.SINGLE_IMAGE_POST for post in posts))

        post_data = None
        for post in posts:
            if post["path"] == self.SINGLE_IMAGE_POST:
                post_data = post["data"]
                break

        self.assertEqual(post_data.get("description", ""), self.EXPECTED_DESCRIPTION)
        self.assertTrue(len(post_data.get("photo_urls", [])) == 1)
        self.assertEqual(post_data.get("photo_urls", [])[0], self.EXPECTED_IMAGE_URL)
