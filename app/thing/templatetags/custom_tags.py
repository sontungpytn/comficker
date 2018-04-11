from django import template
from django.utils.safestring import mark_safe

from app.general.models import ContentType
from app.thing.models import Classify, Field

register = template.Library()


@register.simple_tag
def get_data_value(data, order):
    if order == 'first' or order == 'second':
        if data.get("first") == '' or data.get("second") == '':
            return "-"
    if order == "first":
        output = data.get("first")
    elif order == "second":
        output = data.get("second")
    else:
        output = data
    if data.get('type') == "list":
        data = ""
        for data_temp in output.get('data'):
            data = data + data_temp + ", "
        return mark_safe(data[:-2])
    elif output.get('type') == "image":
        if type(output) is dict:
            image = '<a href="' + output.get('data').get('full_size') + '"'
            image = image + 'data-fancybox data-caption="' + data.get('name') + '">'
            image = image + '<img class="property-img" src="' + output.get('data').get(
                'medium_square_crop') + '" alt="' + data.get(
                'name') + '">'
            image = image + '</a>'
            return mark_safe(image)
        else:
            data = '<img src="' + output + '"alt="' + data.get('name') + '">'
            return mark_safe(data)
    else:
        return mark_safe(output.get('data'))


@register.simple_tag
def get_meta_description(fields):
    data_temp = []
    for field in fields:
        data_temp.append(field.name)
    data = ", ".join(data_temp)
    return mark_safe(data)


@register.simple_tag
def classifies():
    return Classify.objects.all().filter(parent__isnull=True).order_by('id')


def get_deep(dict_data, deep):
    if type(dict_data.get('data')) is list:
        if len(dict_data.get('data')) == 0:
            deep = deep + 1
        for temp in dict_data.get('data'):
            deep = get_deep(temp, deep)
    return deep
