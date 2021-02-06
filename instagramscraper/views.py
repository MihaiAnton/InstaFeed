from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .instagramscraper import InstagramScraper
from bs4 import BeautifulSoup
import os
import selenium.webdriver as webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime, timedelta
from .tasks import scrap_and_check_for_updates, send_daily_updates_email


def index(request):
    try:
        scraper = InstagramScraper(os.environ.get("INSTAGRAM_USERNAME"),
                                   os.environ.get("INSTAGRAM_PASSWORD"))
        data = scraper.scrape_post("/p/CBYzTySjak1/")

        del scraper
    except Exception as err:
        print(err)

    response = JsonResponse(data)
    response.status_code = 200
    return response


def mail(request):
    send_daily_updates_email.delay()

    response = JsonResponse({})
    response.status_code = 200
    return response


def scrape_once(request):
    scrap_and_check_for_updates.delay()

    response = JsonResponse({})
    response.status_code = 200
    return response
