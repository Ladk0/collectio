from django.views import generic
from django.shortcuts import redirect, render

from users.forms import RegisterForm, UserProfileForm
from movies.models import Movie
from tv_shows.models import TvShow

from users.forms import UserProfileForm

class IndexView(generic.TemplateView):
    template_name = 'collectio/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['poster_base_url'] = 'https://image.tmdb.org/t/p/w500/'
        context['movies'] = Movie.objects.all().order_by('-popularity')[:5]
        context['tv_shows'] = TvShow.objects.all().order_by('-popularity')[:5]

        return context


def register(request):
    if request.method == 'POST':
        user_form = RegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.instance.user = user_form.instance
            profile_form.save()
            return redirect(to='login')
    else:
        user_form = RegisterForm()
        profile_form = UserProfileForm()

    return render(request, 'registration/register.html', {'user_form': user_form, 'profile_form': profile_form})
