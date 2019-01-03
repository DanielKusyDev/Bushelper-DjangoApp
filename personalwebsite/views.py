from django.shortcuts import render


def index(request):
    return render(request, 'personalwebsite/index.html')


def error_404(request):
    return render(request, 'http_errors/not_found_404.html')