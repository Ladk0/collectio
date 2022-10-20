from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic
from django.shortcuts import redirect, render

from users.forms import UserProfileForm, UserUpdateForm


class UserDetailView(generic.DetailView):
    model = User
    slug_field = 'username'
    template_name = 'users/user_detail.html'

    def get_context_data(self, **kwargs):
        user = self.object
        context = super().get_context_data(**kwargs)

        user_movies = user.usermovie_set.all()
        movies_status = self.get_items_status(user_movies)
        user_tv_shows = user.usertvshow_set.all()
        tv_shows_status = self.get_items_status(user_tv_shows)

        context['poster_base_url'] = 'https://image.tmdb.org/t/p/w500/'
        context['items'] = [
            {
                'title': 'Movies',
                'name': 'movie',
                'statuses': movies_status,
                'list': [(user_movie.movie, user_movie.status) for user_movie in user_movies[:5]],
                'url': reverse('user_movie-list', args=[user.username])
            },
            {
                'title': 'TV Shows',
                'name': 'tv_show',
                'statuses': tv_shows_status,
                'list': [(user_tv_show.tv_show, user_tv_show.status) for user_tv_show in user_tv_shows[:5]],
                'url': reverse('user_tv_show-list', args=[user.username])
            }
        ]

        return context

    @staticmethod
    def get_items_status(item_set):
        items_status = []
        status_choices = item_set.model.STATUS_CHOICES
        n = len(item_set)
        for status, _ in status_choices:
            count = item_set.filter(status=status).count()
            items_status.append((status, count, ((count / n) * 100) if n != 0 else 0))

        return items_status

@login_required
def update_user(request, slug):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(to='user-detail', slug=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'users/user_form.html', {'user_form': user_form, 'profile_form': profile_form})
