from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from movies.models import Genre, Person, Role

class TvShow(models.Model):
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
    first_air_date = models.DateField(null=True)
    last_air_date = models.DateField(null=True)
    poster_path = models.CharField(max_length=256, blank=True, null=True)
    backdrop_path = models.CharField(max_length=256, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=RELEASED)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True, null=True)
    popularity = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)

    @property
    def seasons(self):
        return self.season_set.all().order_by('number')

    def __str__(self):
        return self.title

class Season(models.Model):
    title = models.CharField(max_length=256)
    overview = models.TextField(max_length=1024, blank=True, null=True)
    poster_path = models.CharField(max_length=256, blank=True, null=True)
    number = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)

    tv_show = models.ForeignKey('TvShow', on_delete=models.CASCADE)

    @property
    def first_air_date(self):
        episode = Episode.objects.filter(season=self).order_by('air_date').first()
        return episode.air_date if episode else None

    @property
    def last_air_date(self):
        episode = Episode.objects.filter(season=self).order_by('air_date').last()
        return episode.air_date if episode else None

    def __str__(self):
        return self.tv_show.title + ', ' + self.title

class Episode(models.Model):
    title = models.CharField(max_length=256)
    overview = models.TextField(max_length=1024, blank=True, null=True)
    air_date = models.DateField(null=True)
    runtime = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    number = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True, null=True)
    poster_path = models.CharField(max_length=256, blank=True, null=True)

    season = models.ForeignKey('Season', on_delete=models.CASCADE)

    def get_human_runtime(self):
        h = self.runtime // 60
        m = self.runtime % 60
        return (f'{h} h. ' if h else '') + (f'{m} m. ' if m else '')

    def __str__(self):
        return self.season.tv_show.title + ', ' + self.season.title + ', ' + self.title


class TvShowGenre(models.Model):
    tv_show = models.ForeignKey('TvShow', on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tv_show.title} is a/an {self.genre.name}'

        
class TvShowPerson(models.Model):
    character = models.CharField(max_length=256, blank=True, null=True)

    tv_show = models.ForeignKey('TvShow', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.tv_show.title}, {self.person.name} {"(" + self.character + ")" if self.role.name == "actor" else ""} as a/an {self.role}'