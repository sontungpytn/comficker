from django.shortcuts import render
from app.thing.models import Compare


def welcome(request):
    new_compare = Compare.objects.all().order_by('-id')[:12]
    return render(request, 'welcome.html', {'comparison': new_compare})


def error_404(request):
    data = {}
    return render(request, 'error/404.html', data)


def error_500(request):
    data = {}
    return render(request, 'error/404.html', data)


def test(request):
    pass