from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.forms import PasswordInput
from django.utils.translation import ugettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(max_length=128, label=_('username'))
    password = forms.CharField(max_length=128, widget=PasswordInput, label=_('password'))

    def authenticate_user(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        return authenticate(username=username, password=password)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
