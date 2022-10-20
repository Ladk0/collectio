from django.urls import path

from .views import *

urlpatterns = [
    path('tv_shows/', tv_show_list, name='tv_show-list'),
    path('tv_shows/<int:pk>', TvShowDetailView.as_view(), name='tv_show-detail'),
    path('tv_shows/<int:tv_show_id>/seasons/<slug:number>', SeasonDetailView.as_view(), name='season-detail'),
    path('user_tv_show_exists', user_tv_show_exists_ajax, name='user_tv_show-exists'),
    path('u/<str:slug>/tv_shows', UserTvShowListView.as_view(), name='user_tv_show-list'),
    path('u/<str:slug>/tv_shows/add', user_tv_show_create_view_ajax, name='user_tv_show-create'),
    path('get_user_tv_show_update_form_ajax', get_user_tv_show_update_form_ajax, name='user_tv_show-get_update_form'),
    path('get_user_season_update_form_ajax', get_user_season_update_form_ajax, name='user_season-get_update_form'),
    path('u/<str:slug>/tv_shows/edit/<int:pk>', user_tv_show_update_ajax, name='user_tv_show-update'),
    path('u/<str:slug>/tv_shows/<int:user_tv_show_id>/season/<int:pk>/edit', user_season_update_ajax, name='user_season-update'),
    path('u/<str:slug>/tv_shows/delete/<int:pk>', user_tv_show_delete_view_ajax, name='user_tv_show-delete'),
]