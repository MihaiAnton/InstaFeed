from django.urls import path
from .views import index, mail, scrape_once

app_name = 'instagramscraper'

urlpatterns = [
    path('', index, name="index"),
    path('mail/', mail, name="mail"),
    path('scrape/', scrape_once, name="scrape")
]
