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
        for data_temp in output:
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
    return Classify.objects.all().filter(parent__isnull=True)


@register.simple_tag
def get_max_level(data, max_level):
    for temp in data:
        if temp.get('level') > max_level:
            max_level = temp.get('level')
            if type(temp.get('data')) is list:
                if max_level < get_max_level(temp.get('data'), max_level):
                    max_level = get_max_level(temp.get('data'), max_level)
    return max_level


@register.simple_tag
def get_max_level2(data, max_level):
    return get_max_level(data, max_level) + 2


@register.simple_tag
def get_max_level3(data, max_level):
    return get_max_level(data, max_level)


@register.simple_tag
def get_current_level(max_level, level):
    return max_level - level


@register.simple_tag
def get_children_number(data, number):
    field = Field.objects.get(name__exact=data.get('name'))
    return field.child().__len__(), data.get('level')


@register.simple_tag
def get_col_row(data, number, max_level):
    children = get_children_number(data, number)[0]
    level = get_children_number(data, number)[1]
    if children == 0:
        col = max_level - level
        row = children + 1
        status = True
    else:
        status = False
        col = 1
        row = children + 1
    return {'row': row, 'col': col, 'status': status }

