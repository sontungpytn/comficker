import itertools
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.text import slugify
from .models import Classify, Thing, Compare


# Create your views here.


def get_field_data(field, first, second, level):
    data = []
    data_content = {'name': field.name, 'first': {}, 'second': {}, 'level': level, 'data': []}
    level = level + 1

    for d in first.data:
        if slugify(d.get('name')) == slugify(field.name):
            data_content['first'] = d
    for d in second.data:
        if slugify(d.get('name')) == slugify(field.name):
            data_content['second'] = d

    for f in field.childs():
        data_content['data'] = data_content.get('data') + get_field_data(f, first, second, level)[0]
    data.append(data_content)
    return data, level


def get_compare_data(first, second):
    if (first.classify.allow_foreign_compare and second.classify.allow_foreign_compare) or (
            first.classify.id == second.classify.id):
        data = []
        list_classify = []
        if first.classify.id == second.classify.id:
            list_classify.append(first.classify)
            list_classify = list_classify + first.classify.parents()
        else:
            list_classify.append(first.classify)
            list_classify = list_classify + first.classify.parents()
            list_classify.append(second.classify)
            list_classify = list_classify + second.classify.parents()
            list_classify = list(set(list_classify))
        list_classify.sort(key=lambda x: x.id)
        for classify in list_classify:
            sub_data = {'name': classify.name, 'data': [], 'level': 1}
            for field in classify.fields():
                temp = get_field_data(field, first, second, 2)[0]
                sub_data['data'] = sub_data['data'] + temp
            data.append(sub_data)
        return {'data': data, 'level': 0}
    else:
        return {}


def thing_show(request, slug):
    classify = get_object_or_404(Classify, slug=slug)
    classify_allow = []
    classify_normal = []
    classify_normal_things = []

    if classify.allow_foreign_compare:
        classify_allow = [classify]
    else:
        classify_normal = [classify]

    for child in classify.child():
        if child.allow_foreign_compare:
            classify_allow.append(child)
        else:
            classify_normal.append(child)

    comparison = list()

    for classify_temp in classify_normal:
        comparison = comparison + list(itertools.combinations(classify_temp.things(), 2))

    for classify_temp in classify_allow:
        classify_normal_things = classify_normal_things + list(classify_temp.things())
    classify_normal_things.sort(key=lambda x: x.name)
    comparison = comparison + list(itertools.combinations(classify_normal_things, 2))

    paginator = Paginator(comparison, 8)
    page = request.GET.get('page')
    try:
        list_images = paginator.page(page)
    except PageNotAnInteger:
        list_images = paginator.page(1)
    except EmptyPage:
        list_images = paginator.page(paginator.num_pages)

    return render(request, 'classify.html', {'classify': classify, 'comparison': list_images})


def thing_compare(request, slug, first, second):
    classify = get_object_or_404(Classify, slug=slug)
    first_thing = get_object_or_404(Thing, slug=first)
    second_thing = get_object_or_404(Thing, slug=second)
    # return HttpResponse(json.dumps(get_compare_data(first_thing, second_thing)))
    compare = Compare.objects.filter(first=first_thing, second=second_thing).first()
    if compare is None:
        if first_thing.name == second_thing.name:
            return HttpResponse("DUB")
        elif first_thing.name > second_thing.name:
            return HttpResponseRedirect('/' + slug + '/' + second_thing.slug + '-and-' + first_thing.slug)
        else:
            slug_temp = first_thing.slug + '-and-' + second_thing.slug
            compare = Compare(first=first_thing, second=second_thing, classify=classify, slug=slug_temp,
                              data=get_compare_data(first_thing, second_thing))
            compare.save()
    else:
        if first_thing.is_edited or second_thing.is_edited:
            compare.data = get_compare_data(first_thing, second_thing)
            compare.classify = classify
            compare.save()
    return render(request, 'compare.html',
                  {'classify': classify, 'compare': compare})


def thing_comment(request):
    pass


def thing(request, classify_slug, thing_slug):
    classify = get_object_or_404(Classify, slug=classify_slug)
    thing = get_object_or_404(Thing, slug=thing_slug)
    return render(request, 'things.html',
                  {'classify': classify, 'item': thing})


def thing_create(request):
    return render(request, 'create.html', {})


def thing_edit(request, classify_slug, thing_slug):
    classify = get_object_or_404(Classify, slug=classify_slug)
    thing = get_object_or_404(Thing, slug=thing_slug)
    return render(request, 'edit.html',
                  {'classify': classify, 'item': thing})
