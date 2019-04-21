from django.urls import path, include
from apps.users.views import CreateUser, AuthenticationView, ProfileView

app_name = 'users'

urlpatterns = [
    path('account/register/', CreateUser.as_view(), name='register'),
    path('account/login/', AuthenticationView.as_view(), name='login'),
    path('account/logout/', AuthenticationView.as_view(), name='logout'),
    path('account/<slug:username>', ProfileView.as_view(), name='profile_detail')
]
