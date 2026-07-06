from django.urls import path
from .views import get_history, reset_chat

urlpatterns=[
    path("history/", get_history),      #have to implement this properly in views.py to return session history
    path("reset/", reset_chat),         
]