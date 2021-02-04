from django.urls import path
from .views import index

app_name = 'instagramscraper'

urlpatterns = [
    path('', index, name="index")
]
