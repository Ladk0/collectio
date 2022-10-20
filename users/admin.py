from django.contrib import admin

from users.models import UserProfile, UserMovie, UserTvShow, UserSeason

admin.site.register((UserProfile, UserMovie, UserTvShow, UserSeason))
