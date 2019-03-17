from django.contrib.auth.models import User

from apps.users.models import Profile


def profile(request):
    context = {}
    if request.user.is_authenticated:
        context = {"profile": Profile.objects.get(user=request.user)}
    return context
