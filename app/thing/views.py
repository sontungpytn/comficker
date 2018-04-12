import itertools
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.text import slugify
from .models import Classify, Thing, Compare


# Create your views here.


def get_levels(dict_data, levels, width, max_deep):
    outer = dict_data.get('level') - 1
    levels = list(levels)
    active = False
    col_span = 1
    if type(dict_data.get('data')) is list:
        if len(dict_data.get('data')) > 0:
            for data_temp in dict_data.get('data'):
                p_data = get_levels(data_temp, levels, width, max_deep)
                levels = p_data.get("levels")
                width = p_data.get("row_span")
            width = width + 1
        else:
            levels.append(dict_data.get('level'))
            width = width + 1
            col_span = max_deep - dict_data.get('level') + 1
            active = True
    deep = max(levels) - dict_data.get('level')
    return {
        "levels": levels,
        "level_max": max(levels),
        "row_span": width,
        "outer": outer,
        "col_span": col_span,
        "deep": deep + 1,
        "active": active
    }


def convert_data(input_data, output_data, max_deep):
    point = get_levels(input_data, [], 0, max_deep)
    if input_data.get("level") == 0:
        max_deep = point.get("level_max")
    temp_data = {
        "name": input_data.get("name"),
        "first": input_data.get("first"),
        "second": input_data.get("second"),
        "col_span": point.get("col_span"),
        "row_span": point.get("row_span"),
        "level": input_data.get("level"),
        "deep": point.get("deep"),
        "active": point.get("active")
    }
    output_data.append(temp_data)
    for data in input_data.get('data'):
        output_data = convert_data(data, output_data, max_deep)
    return output_data


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

        output = {'data': data, 'level': 0}
        # return output
        return convert_data(output, [], 0)
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
    if first_thing.classify.master_parent().id != second_thing.classify.master_parent().id:
        message = first_thing.name + " and " + \
                  second_thing.name + " are two different categories, therefore we can't compare their for you!"
        return render(request, 'layout/error.html', {"title": "Sorry, we can't....", "message": message})
    if first_thing.name == second_thing.name:
        message = "We can't compare " + first_thing.name + " with itself!"
        return render(request, 'layout/error.html', {'title': "Sorry, we can't....", 'message': message})

    if first_thing.classify.id != second_thing.classify.id:
        if not (first_thing.classify.allow_foreign_compare and second_thing.classify.allow_foreign_compare):
            message = first_thing.name + " and " + second_thing.name + " can't compare!"
            return render(request, 'layout/error.html', {'title': "Sorry, we can't....", 'message': message})

    compare = Compare.objects.filter(first=first_thing, second=second_thing).first()
    if compare is None:
        if first_thing.name > second_thing.name:
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
    thing_obj = get_object_or_404(Thing, slug=thing_slug)
    if thing_obj.classify.master_parent().id == classify.master_parent().id:
        if classify.parent is None:
            return render(request, 'things.html', {'classify': classify, 'item': thing_obj})
        else:
            return HttpResponseRedirect('/' + classify.master_parent().slug + '/item/' + thing_obj.slug)
    message = "This does not exist in the system!"
    return render(request, 'layout/error.html', {"title": "404", "message": message})


def thing_create(request):
    if request.user.is_authenticated:
        return render(request, 'create.html', {})
    else:
        message = "Sorry, just member can do this action!"
        return render(request, 'layout/error.html', {"title": "Login required!", "message": message})


def thing_edit(request, classify_slug, thing_slug):
    if request.user.is_authenticated:
        classify = get_object_or_404(Classify, slug=classify_slug)
        thing_obj = get_object_or_404(Thing, slug=thing_slug)
        if thing_obj.creator.id == request.user.id:
            return render(request, 'edit.html', {'classify': classify, 'item': thing_obj})
        else:
            message = "Sorry, creator don't allow you edit this thing!"
            return render(request, 'layout/error.html', {"title": "Permission alert!", "message": message})
    else:
        message = "Sorry, just member can do this action!"
        return render(request, 'layout/error.html', {"title": "Login required!", "message": message})