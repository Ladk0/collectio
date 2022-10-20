from django.urls import path

from .views import *

urlpatterns = [
    path('<str:slug>/', UserDetailView.as_view(), name='user-detail'),
    path('<str:slug>/edit', update_user, name='user-update'),
]
