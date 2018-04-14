from django.shortcuts import render
from app.thing.models import Compare


def welcome(request):
    return render(request, 'welcome.html', {})


def error_404(request):
    data = {}
    return render(request, 'error/404.html', data)


def error_500(request):
    data = {}
    return render(request, 'error/404.html', data)


def test(request):
    pass