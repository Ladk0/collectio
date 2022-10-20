from django.contrib import admin

from tv_shows.models import TvShow, TvShowGenre, TvShowPerson, Season, Episode

admin.site.register((TvShow, TvShowGenre, TvShowPerson, Season, Episode))
