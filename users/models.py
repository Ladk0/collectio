from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='users/images/', default='users/images/default.png', blank=True)

    def __str__(self):  
          return f"{self.user}'s profile"


class UserMovie(models.Model):
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ('-pk',)

    WATCHED = 'watched'
    WATCHING = 'watching'
    PLANNING = 'planning'
    ON_HOLD = 'on-hold'
    DROPPED = 'dropped'

    STATUS_CHOICES = (
        (WATCHED, 'watched'),
        (WATCHING, 'watching'),
        (PLANNING, 'planning'),
        (ON_HOLD, 'on-hold'),
        (DROPPED, 'dropped'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, db_column='tmdb_id')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WATCHED)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)
    comment = models.TextField(max_length=1024, null=True, blank=True)
    date_watched = models.DateField(null=True, blank=True, validators=[MinValueValidator(datetime(1895, 12, 28).date())])
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} has {self.movie}'


class UserTvShow(models.Model):
    class Meta:
        unique_together = ['user', 'tv_show']
        ordering = ('-pk',)

    WATCHED = 'watched'
    WATCHING = 'watching'
    PLANNING = 'planning'
    ON_HOLD = 'on-hold'
    DROPPED = 'dropped'

    STATUS_CHOICES = (
        (WATCHED, 'watched'),
        (WATCHING, 'watching'),
        (PLANNING, 'planning'),
        (ON_HOLD, 'on-hold'),
        (DROPPED, 'dropped'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tv_show = models.ForeignKey('tv_shows.TvShow', on_delete=models.CASCADE, db_column='tmdb_id')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WATCHED)
    comment = models.TextField(max_length=1024, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} has {self.tv_show}'

    @property
    def get_date_updated(self):
        recently_updated_season = self.user_seasons.order_by('-date_updated').first()
        return self.date_updated if self.date_updated > recently_updated_season.date_updated else recently_updated_season.date_updated

    @property
    def user_seasons(self):
        return UserSeason.objects.filter(user=self.user, season__tv_show=self.tv_show)

    @property
    def date_started(self):
        first_season = self.user_seasons.exclude(date_started__isnull=True).order_by('date_started').first()
        return first_season.date_started if first_season else None

    @property
    def date_finished(self):
        last_season = self.user_seasons.exclude(date_finished__isnull=True).order_by('date_finished').last()
        return last_season.date_finished if last_season else None

    @property
    def avg_rating(self):
        ratings = [user_season.rating for user_season in self.user_seasons if user_season.rating]
        return round(sum(ratings)/len(ratings), 2) if ratings else None

class UserSeason(models.Model):
    class Meta:
        unique_together = ['user', 'season']

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    season = models.ForeignKey('tv_shows.Season', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)
    episodes_watched = models.IntegerField(validators=[MinValueValidator(0)], blank=True, default=0)
    comment = models.TextField(max_length=1024, null=True, blank=True)
    date_started = models.DateField(null=True, blank=True, validators=[MinValueValidator(datetime(1928, 9, 11).date())])
    date_finished = models.DateField(null=True, blank=True, validators=[MinValueValidator(datetime(1928, 9, 11).date())])
    date_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.user.username} has {self.season.tv_show.title}: {self.season.title}'
