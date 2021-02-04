from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .instagramscraper import InstagramScraper
from bs4 import BeautifulSoup
import os


def index(request):
    scraper = InstagramScraper(os.environ.get("INSTAGRAM_USERNAME"),
                               os.environ.get("INSTAGRAM_PASSWORD"))
    data = scraper.scrape_post("/p/BIcmEkkBx9u/")

    response = JsonResponse(data)
    response.status_code = 200
    return response
