"""
Definition of urlpatterns.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Handle data news in the past
    path('handle-data-past', views.handle_data_news_past, name='handle_data_news_past'),
    
    # Handle data news daily
    path('handle-data-daily', views.handle_data_news_daily, name='handle_data_news_daily'),
    
    path('test-sentence-weight', views.get_test_sentence_weight, name='get_test_sentence_weight'),
]
