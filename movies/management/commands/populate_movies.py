from movies.models import Movie, MovieGenre, Genre, MoviePerson, Person, Role
from tv_shows.models import TvShow, TvShowGenre, TvShowPerson, Season, Episode
from movies.views import tmdb

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Populates movies in the database by calling the TMDB api'

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
        self.populate_movies(pages)
        return

    def populate_movies(self, pages):
        n = 0
        for i in range(pages):
            movies = tmdb.Movies().popular(page=i+1)['results']
            for popular_movie in movies:
                n += 1
                tmdb_movie = tmdb.Movies(popular_movie['id']).info()
                if tmdb_movie['adult']:
                    self.stdout.write('Skipped adult movie: ' + tmdb_movie['title'])
                    continue
                self.stdout.write(str(n) + '. ' + tmdb_movie['title'])
                tmdb_genres = tmdb_movie['genres']
                tmdb_movie['tmdb_id'] = tmdb_movie.pop('id')
                tmdb_movie['rating'] = tmdb_movie.pop('vote_average')
                movie_fields = [field.name for field in Movie._meta.get_fields()]
                for field, value in list(tmdb_movie.items()):
                    if field not in movie_fields or not value:
                        tmdb_movie.pop(field)
                
                try:
                    movie = Movie.objects.get(tmdb_id=tmdb_movie['tmdb_id'])
                except Movie.DoesNotExist:
                    movie = Movie(**tmdb_movie)
                    movie.save()
                
                temp_genres = []
                for genre in tmdb_genres:
                    if '&' in genre['name']:
                        temp_genres.extend(genre['name'].split('&'))
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
                        MovieGenre.objects.get(movie=movie, genre=genre)
                    except MovieGenre.DoesNotExist:
                        MovieGenre(movie=movie, genre=genre).save()

                credits = tmdb.Movies(popular_movie['id']).credits()
                
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
                            MoviePerson.objects.get(movie=movie, person=person)
                        except MoviePerson.DoesNotExist:
                            MoviePerson(movie=movie, person=person, character=cast['character'], role=Role.objects.get(name='actor')).save()
                
                cast_num = 0
                for cast in credits['crew']:
                    if cast.get('job') == 'Director':
                        cast_num += 1
                        if cast_num > cast_max:
                            break
                        try:
                            person = Person.objects.get(name=cast['name'])
                        except Person.DoesNotExist:
                            person = Person(name=cast['name'])
                            person.save()
                        
                        try:
                            MoviePerson.objects.get(movie=movie, person=person)
                        except MoviePerson.DoesNotExist:
                            MoviePerson(movie=movie, person=person, role=Role.objects.get(name='director')).save()
