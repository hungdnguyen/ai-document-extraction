from django.urls import path
from .views import parseFile

urlpatterns = [
    path('parseFile/', parseFile, name='parseFile'),
]