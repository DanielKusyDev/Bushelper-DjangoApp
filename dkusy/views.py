from django.shortcuts import render


def not_found_404(request):
    return render(request, 'http_errors/not_found_404.html')


def bad_request_400(request):
    return render(request, 'http_errors/bad_request_400.html')


def server_error_500(request):
    return render(request, 'http_errors/server_error_500.html')
