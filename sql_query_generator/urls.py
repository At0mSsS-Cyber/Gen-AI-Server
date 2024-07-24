from django.urls import path
from .views import query_database

urlpatterns = [
    path('query/', query_database, name='query_database'),
]
