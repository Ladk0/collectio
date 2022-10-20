import datetime
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.http import JsonResponse, QueryDict
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from tv_shows.models import Season, TvShow
from tv_shows.forms import UserTvShowCreateForm, UserSeasonEditForm
from movies.models import Genre
from users.models import UserTvShow, UserSeason

from movies.views import poster_base_url, poster_sizes

def tv_show_list(request):
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

        tv_shows = TvShow.objects \
            .filter(title__icontains=q) \
            .order_by('-rating' if sort_by == 'rating' else '-popularity')
        
        if min_date:
            min_date = datetime.datetime.fromisoformat(min_date)
            tv_shows = tv_shows.filter(first_air_date__gte=min_date)
        if max_date:
            max_date = datetime.datetime.fromisoformat(max_date)
            tv_shows = tv_shows.filter(first_air_date__lte=max_date)


        if genres:
            tv_shows = [tv_show for tv_show in tv_shows if all([genre in [tv_show_genre.genre for tv_show_genre in tv_show.tvshowgenre_set.all()] for genre in genres])]

        paginator = Paginator(tv_shows, 20)

        try:
            tv_shows = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            tv_shows = None
        
        context['tv_shows'] = tv_shows

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'tv_shows/cards.html', context)

        return render(request, 'tv_shows/tv_show_list.html', context)


class TvShowDetailView(generic.DetailView):
    model = TvShow
    template_name = 'tv_shows/tv_show_detail.html'
    context_object_name = 'tv_show'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        tv_show_persons = self.object.tvshowperson_set
        directors = [tv_show_person.person.name for tv_show_person in tv_show_persons.filter(role__name='director').all()]
        actors = {tv_show_person.person.name: tv_show_person.character for tv_show_person in tv_show_persons.filter(role__name='actor').all()[:10]}

        context['poster_base_url'] = poster_base_url
        context['poster_sizes'] = poster_sizes
        context['directors'] = directors
        context['actors'] = actors

        return context

class UserTvShowListView(LoginRequiredMixin, generic.ListView):
    model = UserTvShow
    slug_field = 'username'
    template_name = 'user_tv_shows/user_tv_show_list.html'
    context_object_name = 'user_tv_shows'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poster_base_url'] = poster_base_url
        context['poster_sizes'] = poster_sizes
        context['sort_fields'] = {
            'name': 'Name',
            'rating': 'Average rating',
            'first_air_date': 'First air date',
            'last_air_date': 'Last air date',
            'date_started': 'Started',
            'date_finished': 'Finished',
            'date_added': 'Added',
            'date_updated': 'Updated'
        }

        return context

    def get_queryset(self):
        user = self.request.user
        user_tv_shows = UserTvShow.objects.filter(user=user).all()

        return user_tv_shows

def user_tv_show_exists_ajax(request):
    user = User.objects.get(username=request.GET.get('username', None))
    tv_show = TvShow.objects.get(tmdb_id=request.GET.get('tmdb_id', None))
    if UserTvShow.objects.filter(user=user, tv_show=tv_show).exists():
        return JsonResponse({'exists': True}, status=200)
    else:
        form = UserTvShowCreateForm(initial={'user':user, 'tv_show':tv_show})
        return render(request, 'user_tv_shows/user_tv_show_form.html', {'form': form})

def user_tv_show_create_view_ajax(request, slug=None):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = UserTvShowCreateForm(QueryDict(request.body) or None)
        if form.is_valid():
            form.save()
            for s in form.instance.tv_show.season_set.all():
                UserSeason(user=form.instance.user, season=s).save()
            return JsonResponse({"success": True}, status=200)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)

def get_user_tv_show_update_form_ajax(request):
    pk = request.GET.get('id', None)
    form = UserTvShowCreateForm(instance=UserTvShow.objects.get(pk=pk))
    return render(request, 'user_tv_shows/user_tv_show_form.html', {'form': form})

def get_user_season_update_form_ajax(request):
    pk = request.GET.get('id', None)
    form = UserSeasonEditForm(instance=UserSeason.objects.get(pk=pk))
    return render(request, 'user_tv_shows/user_season_form.html', {'form': form})

def user_tv_show_update_ajax(request, slug, pk):
    if request.method == 'PATCH' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user = User.objects.get(username__iexact=slug)
        user_tv_show = get_object_or_404(UserTvShow, pk=pk, user=user)
        form = UserTvShowCreateForm(QueryDict(request.body) or None, instance = user_tv_show)
        if form.is_valid():
            form.save()
            data = {field:form.cleaned_data[field] for field in form.changed_data}
            return JsonResponse(data, status=200)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)

def user_season_update_ajax(request, slug, user_tv_show_id, pk):
    if request.method == 'PATCH' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user = User.objects.get(username__iexact=slug)
        user_season = get_object_or_404(UserSeason, pk=pk, user=user)
        user_tv_show = UserTvShow.objects.get(pk=user_tv_show_id)
        form = UserSeasonEditForm(QueryDict(request.body) or None, instance = user_season)
        if form.is_valid():
            form.save()
            data = {field:form.cleaned_data[field] for field in form.changed_data}
            if 'rating' in data.keys():
                data['avg_rating'] = user_tv_show.avg_rating
            if 'date_started' in data.keys():
                data['parent_date_started'] = user_tv_show.date_started
            if 'date_finished' in data.keys():
                data['parent_date_finished'] = user_tv_show.date_finished
            for k, v in data.items():
                if isinstance(v, datetime.date):
                    data[k] = v.strftime("%b %d, %Y")
            data['date_updated'] = user_tv_show.get_date_updated.strftime('%b %d, %Y, %I:%M') + ' ' + ('a.m.' if user_tv_show.get_date_updated.strftime('%p')=='AM' else 'p.m.')
            data['date_added'] = user_tv_show.date_created.strftime('%b %d, %Y, %I:%M') + ' ' + ('a.m.' if user_tv_show.date_created.strftime('%p')=='AM' else 'p.m.')
            return JsonResponse(data, status=200)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)

def user_tv_show_delete_view_ajax(request, slug, pk):
    if request.method == "DELETE" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user = User.objects.get(username__iexact=slug)
        user_tv_show = get_object_or_404(UserTvShow, pk=pk, user=user)
        for s in user_tv_show.tv_show.season_set.all():
            UserSeason.objects.get(user=user, season=s).delete()
        user_tv_show.delete()
        return JsonResponse({'success': True}, status=200)

class SeasonDetailView(generic.DetailView):
    model = Season
    slug_field = 'number'
    
    def get_object(self):
        tv_show = TvShow.objects.get(pk=self.kwargs['tv_show_id'])
        season = Season.objects.get(tv_show=tv_show, number=self.kwargs['number'])
        return season

    def get_context_data(self, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['poster_base_url'] = poster_base_url
        context['poster_sizes'] = poster_sizes
        
        return context