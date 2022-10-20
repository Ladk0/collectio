from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Movie(models.Model):
    RUMORED = 'rumored'
    PLANNED = 'planned'
    IN_PRODUCTION = 'in production'
    POST_PRODUCTION = 'post production'
    RELEASED = 'released'
    CANCELED = 'canceled'

    STATUS_CHOICES = (
        (RUMORED, 'rumored'),
        (PLANNED, 'planned'),
        (IN_PRODUCTION, 'in production'),
        (POST_PRODUCTION, 'post production'),
        (RELEASED, 'released'),
        (CANCELED, 'canceled')
    )

    tmdb_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=256, unique=True)
    overview = models.TextField(max_length=1024, blank=True, null=True)
    release_date = models.DateField()
    runtime = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    budget = models.BigIntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    revenue = models.BigIntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    poster_path = models.CharField(max_length=256, blank=True, null=True)
    backdrop_path = models.CharField(max_length=256, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=RELEASED)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True, null=True)
    popularity = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)

    def __str__(self):
        return self.title


class MovieGenre(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.movie.title} is a/an {self.genre.name}'


class Genre(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class MoviePerson(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.PROTECT)
    character = models.CharField(max_length=256, blank=True, null=True)
    role = models.ForeignKey('Role', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.movie.title}, {self.person.name} {"(" + self.character + ")" if self.role.name == "actor" else ""} as a/an {self.role}'


class Person(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name
