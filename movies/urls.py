from django.urls import path

from .views import *

urlpatterns = [
    path('movies/', movie_list, name='movie-list'),
    path('movies/<int:pk>', MovieDetailView.as_view(), name='movie-detail'),
    path('user_movie_exists', user_movie_exists_ajax, name='user_movie-exists'),
    path('u/<str:slug>/movies', UserMoviesView.as_view(), name='user_movie-list'),
    path('u/<str:slug>/movies/add', user_movie_create_view_ajax, name='user_movie-create'),
    path('get_user_movie_update_form_ajax', get_user_movie_update_form_ajax, name='user_movie-get_update_form'),
    path('u/<str:slug>/movies/edit/<int:pk>', user_movie_update_ajax, name='user_movie-update'),
    path('u/<str:slug>/movies/delete/<int:pk>', user_movie_delete_view_ajax, name='user_movie-delete'),
]