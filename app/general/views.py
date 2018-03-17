from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.apps import apps
from .models import ContentType
from django.http import HttpResponse
# Create your views here.


def user_index(request):
    users_list = User.objects.order_by('date_joined')
    paginator = Paginator(users_list, 9)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return render(request, 'user/index.html', {'users': users})


def show_account(request, user_id):
    user = User.objects.filter(pk=user_id).first()
    model_types = ContentType.objects.all()
    categories = []
    for model_type in model_types:
        categories.append({
            'name': model_type.name,
            'posts': apps.get_model('model_' + model_type.slug, 'Model').objects.filter(user=user)})

    return render(request, 'user/account.html', {'user': user, 'categories': categories})


def user_update(request, user_id):
    return render(request, 'user/edit.html')