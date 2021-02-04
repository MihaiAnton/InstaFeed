from .IInstagramScraper import IInstagramScraper
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class InstagramScraper(IInstagramScraper):
    URL = 'https://www.instagram.com/'

    def __init__(self, username, password, login=True):
        self._username = username
        self._password = password
        chrome_options = Options()

        self._driver = webdriver.Remote(command_executor='http://chrome:4444/wd/hub',
                                        desired_capabilities=DesiredCapabilities.CHROME)

        if login:
            self._loggedIn = self.login()

            if not self._loggedIn:
                raise Exception("Could not log into Instagram on init.")
        else:
            self._loggedIn = False

    def __del__(self):
        try:
            self._driver.close()
        except Exception as err:
            pass

    def login(self) -> bool:
        """Logs in Instagram
        """

        try:
            # access instagram
            self._driver.get(self.URL)

            # accept cookies
            try:
                WebDriverWait(self._driver, 4).until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[text()='Accept']"))).click()
            except Exception as err:
                pass

            # complete login form
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable(
                (By.NAME, "username"))).send_keys(self._username)
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable(
                (By.NAME, "password"))).send_keys(self._password)

            # login
            loginXpath = f"//div[@class='                     Igw0E     IwRSH      eGOV_         _4EzTm{' '*110}']"
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.XPATH, loginXpath))).click()

            try:  # don't save login data
                dontSaveXpath = "/html/body/div[1]/section/main/div/div/div/div/button"
                WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.XPATH, dontSaveXpath))).click()
            except Exception as err:
                pass

            try:  # no notifications
                notNowXpath = "/html/body/div[4]/div/div/div/div[3]/button[2]"
                WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.XPATH, notNowXpath))).click()
            except Exception as err:
                pass

            return True
        except Exception as err:
            # TODO log
            return False

    def scrape_profile(self, username: str) -> dict:
        if not self._loggedIn:
            self.login()
        if not self._loggedIn:
            raise Exception(f"Not logged in on scrape: profile={username}")

        self._driver.get(f"{self.URL}{username}/?hl=en")

        post_paths = self._get_post_paths()
        posts = []

        for post_path in post_paths:
            print(f"Getting {post_path}")
            try:
                post_data = self.scrape_post(post_path)
                posts.append({"path": post_path, "data": post_data})
            except Exception as err:
                # TODO log
                pass

        return {"posts": posts}

    def _get_post_paths(self) -> set:
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

    def scrape_post(self, path) -> dict:
        """Scrapes a particular post and returns a dictionary.

        Arguments:
            path {[string]} -- [path to post]

        Returns:
            dict: {description: str, photo_urls: [str]}
        """
        self._driver.get(self.URL + path)

        photo_urls = set()
        description = ""

        _description = self._driver.find_elements_by_xpath("//div[@class='C7I1f X7jCj']//div[@class='C4VMK']//span")
        if len(_description) > 1:
            description = BeautifulSoup(_description[1].get_attribute('innerHTML'), "html.parser").text

        images = self._driver.find_elements_by_xpath("//div[@class='_97aPb wKWK0']//div[@class='KL4Bh']//img")
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
                    images = self._driver.find_elements_by_xpath(
                        "//div[@class='_97aPb wKWK0']//div[@class='KL4Bh']//img")
                    images = [image.get_attribute('src') for image in images]

                    for path in images:
                        photo_urls.add(path)

                except Exception as err:
                    pass

        return {"description": description, "photo_urls": list(photo_urls)}
