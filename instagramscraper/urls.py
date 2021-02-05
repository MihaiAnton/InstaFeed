from django.urls import path
from .views import index, mail

app_name = 'instagramscraper'

urlpatterns = [
    path('', index, name="index"),
    path('mail/', mail, name="mail")
]
