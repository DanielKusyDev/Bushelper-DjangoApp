from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib.auth import logout, get_user_model, login
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from apps.users.forms import LoginForm
from apps.users.models import Profile

PREFIX_TEMPLATE = 'users/templates/'


def get_template_name(name):
    return PREFIX_TEMPLATE + name


class ProfileView(DetailView):
    template_name = get_template_name('profile_detail.html')
    queryset = Profile.objects.all()

    def get_object(self, **kwargs):
        username = self.kwargs.get("username")
        return get_object_or_404(Profile, user=get_user_model().objects.get(username=username))


class CreateUser(View):
    http_method_names = ['get', 'post']

    def get(self, request):
        return render(request, get_template_name('add_user.html'), context={'form': UserCreationForm()})

    def post(self, request):
        user = UserCreationForm(request.POST)
        if user.is_valid():
            messages.add_message(request=request, level=messages.SUCCESS, message='Zarejestrowano pomyślnie')
            user.save()
        else:
            messages.add_message(request=request, level=messages.SUCCESS, message='Błąd rejestracji')
        return redirect(reverse('users:register'))


class AuthenticationView(View):
    http_method_names = ['get', 'post']
    logout_path = '/account/logout'
    template_name = get_template_name('login_page.html')

    def get(self, request):
        if self.logout_path in request.path:
            logout(request)
            return redirect('users:login')
        return render(request, self.template_name, context={'form': LoginForm()})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            return self.authenticate(request, login_form)
        return render(request, self.template_name, context={'form': login_form, 'errors': login_form.errors}, status=401)

    def authenticate(self, request, form):
        user = form.authenticate_user()
        if user is not None:
            login(request, user)
            return redirect(reverse('bushelper:search_engine_view'))
        return render(request, self.template_name, context={'form': form, 'errors': {'auth_error': _('Nieprawidłowe dane logowania')}}, status=401)



