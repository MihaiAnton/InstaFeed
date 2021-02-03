from .IInstagramScraper import IInstagramScraper
from ..models import Profile, Post
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


class InstagramScraper(IInstagramScraper):
    URL = 'https://www.instagram.com/'

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._driver = webdriver.Chrome()
        self._loggedIn = self.login()

        if not self._loggedIn:
            raise Exception("Could not log into Instagram on init.")

    def login(self) -> bool:
        """Logs in Instagram
        """

        try:
            # access instagram
            self._driver = webdriver.Chrome()
            self._driver.get(self.URL)

            # accept cookies
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Accept']"))).click()

            # complete login form
            self._driver.find_element_by_name("username").send_keys(self._username)
            self._driver.find_element_by_name("password").send_keys(self._password)

            # login
            loginXpath = f"//div[@class='                     Igw0E     IwRSH      eGOV_         _4EzTm{' '*110}']"
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.XPATH, loginXpath))).click()

            # don't save login info
            dontSaveXpath = "/html/body/div[1]/section/main/div/div/div/div/button"
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.XPATH, dontSaveXpath))).click()

            # close notifications popup
            notNowXpath = "/html/body/div[4]/div/div/div/div[3]/button[2]"
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.XPATH, notNowXpath))).click()
            return True
        except Exception as err:
            # TODO log
            return False

    def scrape_profile(self, username: str) -> dict:
        if not self._loggedIn:
            self.login()
        if not self._loggedIn:
            return Profile(username=username, accessible=False)

        post_paths = self._get_post_paths()
        posts = []

        for post_path in post_paths:
            try:
                post_data = self._scrape_post(post_path)
                posts.append({"path": post_path, "data": post_data})
            except Exception as err:
                # TODO log
                pass

        return {"posts": posts}

    def _get_post_paths(self) -> set[str]:
        """Returns a list with the paths of each post

        Returns:
            list[str] -- [description]
        """
        SCROLL_PAUSE_TIME = 4

        post_paths = set()

        last_height = self._driver.execute_script("return document.body.scrollHeight")
        while True:
            posts = self._driver.find_elements_by_xpath("//div[@class='v1Nh3 kIKUG  _bz0w']")
            for post in posts:
                soup = BeautifulSoup(post.get_attribute('innerHTML'), "html.parser")
                post_paths.add(soup.a["href"])

            # Scroll down to bottom
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self._driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return post_paths

    def _scrape_post(self, path) -> dict:
        """Scrapes a particular post and returns a dictionary.

        Arguments:
            path {[string]} -- [path to post]

        Returns:
            dict: {description: str, photo_urls: [str]}
        """
        photo_urls = set()
        description = ""

        _description = self._driver.find_elements_by_xpath("//div[@class='C4VMK']//span")
        if len(_description) > 1:
            description = BeautifulSoup(_description[1].get_attribute('innerHTML')).text

        images = self._driver.find_elements_by_xpath("//li[@class='Ckrof']//img")
        images = [image.get_attribute('src') for image in images]

        for path in images:
            photo_urls.add(path)

        has_next = True
        while has_next:     # click next and get photos as long as it's possible
            try:
                next_photo_xpath = "//div[@class='    coreSpriteRightChevron  ']"
                WebDriverWait(self._driver, 0.5).until(EC.element_to_be_clickable((By.XPATH, next_photo_xpath))).click()
            except Exception as err:
                has_next = False

            if has_next:
                try:
                    images = self._driver.find_elements_by_xpath("//li[@class='Ckrof']//img")
                    images = [image.get_attribute('src') for image in images]

                    for path in images:
                        photo_urls.add(path)

                except Exception as err:
                    pass

        return {"desription": description, "photo_urls": list[photo_urls]}
