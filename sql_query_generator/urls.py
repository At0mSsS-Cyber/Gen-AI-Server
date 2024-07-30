from django.urls import path
from .views import query_database, list_tables, sample_data

urlpatterns = [
    path('query/', query_database, name='query_database'),
    path('api/tables/', list_tables),
    path('api/tables/<str:table_name>/', sample_data),
]
