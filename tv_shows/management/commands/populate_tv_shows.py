from movies.models import Movie, MovieGenre, Genre, MoviePerson, Person, Role
from tv_shows.models import TvShow, TvShowGenre, TvShowPerson, Season, Episode
from movies.views import tmdb

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Populates the tv shows in the database by calling the TMDB api'

    def add_arguments(self, parser):
        parser.add_argument('pages', type=int)
        
    def handle(self, *args, **kwargs):
        pages = kwargs['pages']
        try:
            Role.objects.get(name='actor')
        except Role.DoesNotExist:
            Role(name='actor').save()
        try:
            Role.objects.get(name='director')
        except Role.DoesNotExist:
            Role(name='director').save()
        self.populate_tv_shows(pages)
        return

    def populate_tv_shows(self, pages):
        n = 0
        for i in range(pages):
            tv_shows = tmdb.TV().popular(page=i+1)['results']
            for popular_tv_show in tv_shows:
                n += 1
                tmdb_tv_show = tmdb.TV(popular_tv_show['id']).info()
                if tmdb_tv_show['adult']:
                    self.stdout.write('Skipped adult tv show: ' + tmdb_tv_show['name'])
                    continue
                self.stdout.write(str(n) + '. ' + tmdb_tv_show['name'])
                tmdb_genres = tmdb_tv_show['genres']
                created_by = tmdb_tv_show['created_by']
                tmdb_tv_show['tmdb_id'] = tmdb_tv_show.pop('id')
                tmdb_tv_show['rating'] = tmdb_tv_show.pop('vote_average')
                tmdb_tv_show['title'] = tmdb_tv_show.pop('name')
                tmdb_seasons = tmdb_tv_show['seasons']
                tv_show_fields = [field.name for field in TvShow._meta.get_fields()]
                for field, value in list(tmdb_tv_show.items()):
                    if field not in tv_show_fields or not value:
                        tmdb_tv_show.pop(field)
                
                try:
                    tv_show = TvShow.objects.get(tmdb_id=tmdb_tv_show['tmdb_id'])
                except TvShow.DoesNotExist:
                    tv_show = TvShow(**tmdb_tv_show)
                    tv_show.save()
                
                for tmdb_season in tmdb_seasons:
                    self.stdout.write('\t' + tmdb_season['name'])
                    tmdb_season['title'] = tmdb_season.pop('name')
                    tmdb_season['number'] = tmdb_season.pop('season_number')
                    tmdb_season.pop('air_date')
                    tmdb_season.pop('episode_count')
                    try:
                        season = Season.objects.get(tv_show=tv_show, number=tmdb_season['number'])
                    except Season.DoesNotExist:
                        season = Season(**tmdb_season, tv_show=tv_show)
                        season.save()

                    tmdb_episodes = tmdb.TV_Seasons(tv_show.tmdb_id, season.number).info()['episodes']
                    for tmdb_episode in tmdb_episodes:
                        tmdb_episode['title'] = tmdb_episode.pop('name')
                        tmdb_episode['number'] = tmdb_episode.pop('episode_number')
                        tmdb_episode['poster_path'] = tmdb_episode.pop('still_path')
                        tmdb_episode['rating'] = tmdb_episode.pop('vote_average')
                        episode_fields = [field.name for field in Episode._meta.get_fields()]
                        for field in list(tmdb_episode.keys()):
                            if field not in episode_fields:
                                tmdb_episode.pop(field)
                        try:
                            episode = Episode.objects.get(season=season, number=tmdb_episode['number'])
                        except Episode.DoesNotExist:
                            episode = Episode(**tmdb_episode, season=season)
                            episode.save()

                temp_genres = []
                for genre in tmdb_genres:
                    if '&' in genre['name']:
                        genres = [_.strip() for _ in genre['name'].split('&')]
                        temp_genres.extend(genres)
                    else:
                        temp_genres.append(genre['name'])
                tmdb_genres = temp_genres
                
                for genre in tmdb_genres:
                    try:
                        genre = Genre.objects.get(name=genre)
                    except Genre.DoesNotExist:
                        genre = Genre(name=genre)
                        genre.save()
                    
                    try:
                        TvShowGenre.objects.get(tv_show=tv_show, genre=genre)
                    except TvShowGenre.DoesNotExist:
                        TvShowGenre(tv_show=tv_show, genre=genre).save()

                credits = tmdb.TV(popular_tv_show['id']).credits()
                
                cast_max = 3
                cast_num = 0
                for cast in credits['cast']:
                    if cast['known_for_department'] == 'Acting':
                        cast_num += 1
                        if cast_num > cast_max:
                            break
                        try:
                            person = Person.objects.get(name=cast['name'])
                        except Person.DoesNotExist:
                            person = Person(name=cast['name'])
                            person.save()
                        
                        try:
                            TvShowPerson.objects.get(tv_show=tv_show, person=person)
                        except TvShowPerson.DoesNotExist:
                            TvShowPerson(tv_show=tv_show, person=person, character=cast['character'], role=Role.objects.get(name='actor')).save()
                
                cast_num = 0
                for creator in created_by:
                    cast_num += 1
                    if cast_num > cast_max:
                        break
                    try:
                        person = Person.objects.get(name=creator['name'])
                    except Person.DoesNotExist:
                        person = Person(name=creator['name'])
                        person.save()
                    
                    try:
                        TvShowPerson.objects.get(tv_show=tv_show, person=person)
                    except TvShowPerson.DoesNotExist:
                        TvShowPerson(tv_show=tv_show, person=person, role=Role.objects.get(name='director')).save()