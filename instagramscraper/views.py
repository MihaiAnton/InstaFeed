from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .instagramscraper import InstagramScraper
from bs4 import BeautifulSoup
import os
import selenium.webdriver as webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def index(request):
    try:
        scraper = InstagramScraper(os.environ.get("INSTAGRAM_USERNAME"),
                                   os.environ.get("INSTAGRAM_PASSWORD"))
        data = scraper.scrape_profile("mihaianton98")

        del scraper

    except Exception as err:
        print(err)

    response = JsonResponse(data)
    response.status_code = 200
    return response
