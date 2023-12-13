"""
Definition of urlpatterns.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Handle data news in the past
    path('handle-data-past', views.handle_data_news_past, name='handle_data_news_past'),
]
