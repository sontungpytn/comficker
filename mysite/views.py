from django.shortcuts import render
from app.general.models import ContentType


def welcome(request):
    contents = ContentType.objects.all()
    return render(request, 'welcome.html', {'contents': contents})


def error_404(request):
    data = {}
    return render(request, 'error/404.html', data)


def error_500(request):
    data = {}
    return render(request, 'error/404.html', data)