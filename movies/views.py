import datetime
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.http import JsonResponse, QueryDict
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

import tmdbsimple as tmdb

from movies.forms import UserMovieCreateForm
from movies.models import Genre, Movie
from users.models import UserMovie

tmdb.API_KEY = 'f0553f68f9cbb6aa8f90688ecf8be212'

conf = tmdb.configuration.Configuration().info()
poster_base_url = conf['images']['base_url']
poster_sizes = conf['images']['poster_sizes']


def movie_list(request):
        context = {}
        context['poster_base_url'] = poster_base_url
        context['poster_sizes'] = poster_sizes
        context['genres'] = Genre.objects.all()

        q = request.GET.get('search', '')
        sort_by = request.GET.get('sort_by', 'popularity')
        genres = [Genre.objects.get(name=g) for g in request.GET.getlist('genres[]')]
        min_date = request.GET.get('min_date')
        max_date = request.GET.get('max_date')

        page = request.GET.get('page', 1)

        movies = Movie.objects \
            .filter(title__icontains=q) \
            .order_by('-rating' if sort_by == 'rating' else '-popularity')
        
        if min_date:
            min_date = datetime.datetime.fromisoformat(min_date)
            movies = movies.filter(release_date__gte=min_date)
        if max_date:
            max_date = datetime.datetime.fromisoformat(max_date)
            movies = movies.filter(release_date__lte=max_date)


        if genres:
            movies = [movie for movie in movies if all([genre in [moviegenre.genre for moviegenre in movie.moviegenre_set.all()] for genre in genres])]

        paginator = Paginator(movies, 20)

        try:
            movies = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            movies = None
        
        context['movies'] = movies

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'movies/cards.html', context)

        return render(request, 'movies/movie_list.html', context)
    
class MovieDetailView(generic.DetailView):
    model = Movie

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        movie_persons = self.object.movieperson_set
        directors = [movie_person.person.name for movie_person in movie_persons.filter(role__name='director').all()]
        actors = {movie_person.person.name: movie_person.character for movie_person in movie_persons.filter(role__name='actor').all()[:10]}

        context['poster_base_url'] = poster_base_url
        context['poster_sizes'] = poster_sizes
        context['directors'] = directors
        context['actors'] = actors

        return context

class UserMoviesView(LoginRequiredMixin, generic.ListView):
    model = UserMovie
    slug_field = 'username'
    template_name = 'user_movies/user_movie_list.html'
    context_object_name = 'user_movie_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserMovieCreateForm()
        context['poster_base_url'] = poster_base_url
        context['poster_sizes'] = poster_sizes
        context['sort_fields'] = {
            'name': 'Name',
            'rating': 'Rating',
            'release_date': 'Release date',
            'date_watched': 'Date watched',
            'date_added': 'Date added',
            'date_updated': 'Date updated'
        }

        return context

    def get_queryset(self):
        user = self.request.user
        user_movies = UserMovie.objects.filter(user=user).all()

        return user_movies

def user_movie_exists_ajax(request):
    user = User.objects.get(username=request.GET.get('username', None))
    movie = Movie.objects.get(tmdb_id=request.GET.get('tmdb_id', None))
    if UserMovie.objects.filter(user=user, movie=movie).exists():
        return JsonResponse({'exists': True}, status=200)
    else:
        form = UserMovieCreateForm(initial={'user':user, 'movie':movie})
        return render(request, 'user_movies/user_movie_form.html', {'form': form})

def user_movie_create_view_ajax(request, slug=None):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = UserMovieCreateForm(QueryDict(request.body) or None)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True}, status=200)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)

def get_user_movie_update_form_ajax(request):
    pk = request.GET.get('id', None)
    form = UserMovieCreateForm(instance=UserMovie.objects.get(pk=pk))
    return render(request, 'user_movies/user_movie_form.html', {'form': form})

def user_movie_update_ajax(request, slug, pk):
    if request.method == 'PATCH' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_movie = get_object_or_404(UserMovie, pk=pk, user__username=slug)
        form = UserMovieCreateForm(QueryDict(request.body) or None, instance = user_movie)
        if form.is_valid():
            form.save()
            data = {field:form.cleaned_data[field] for field in form.changed_data}
            for k, v in data.items():
                if isinstance(v, datetime.date):
                    data[k] = v.strftime("%b %d, %Y")
            return JsonResponse(data, status=200)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)


def user_movie_delete_view_ajax(request, slug, pk):
    if request.method == "DELETE" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_movie = get_object_or_404(UserMovie, user__username__iexact=slug, pk=pk)
        user_movie.delete()
        return JsonResponse({'success': True}, status=200)
