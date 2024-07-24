from django.urls import path
from .views import process_urls, ask_question

urlpatterns = [
    path('process_urls/', process_urls, name='process_urls'),
    path('ask_question/', ask_question, name='ask_question'),
]
