from django.urls import path, include
from apps.users.views import CreateUser, AuthenticationView

app_name = 'users'

urlpatterns = [
    path('account/register', CreateUser.as_view(), name='register'),
    path('account/login', AuthenticationView.as_view(), name='login')

]
