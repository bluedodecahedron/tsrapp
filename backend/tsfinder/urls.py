from django.urls import path
from . import views

urlpatterns = [
    path('', views.find_traffic_signs, name='find_traffic_signs'),
]
