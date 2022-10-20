from django.contrib import admin

from movies.models import Movie, MovieGenre, Genre, MoviePerson, Person, Role

admin.site.register((Movie, MovieGenre, Genre, MoviePerson, Person, Role))
