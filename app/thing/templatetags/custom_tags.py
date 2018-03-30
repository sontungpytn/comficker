from django import template
from django.utils.safestring import mark_safe
from app.thing.models import Classify
from app.general.models import ContentType

register = template.Library()


@register.filter(is_safe=True)
def half_slug(value):
    return value.replace(" ", "-")


@register.simple_tag
def get_description(properties):
    for property_temp in properties:
        if property_temp['name'] == "Description":
            return property_temp['data']
    return "..."


@register.simple_tag
def get_value(properties, field, subclass):
    for property_temp in properties:
        if property_temp.get('sub_class') == subclass:
            if property_temp['name'] == field:
                if property_temp.get('type') == 'list':
                    data = ""
                    for data_temp in property_temp['data']:
                        data = data + data_temp + ", "
                    return mark_safe(data[:-2])
                elif property_temp.get('type') == 'image':
                    if type(property_temp.get('data')) is dict:
                        data = '<a href="' + property_temp['data']['full_size'] + '"'
                        data = data + 'data-fancybox data-caption="' + property_temp.get('name') + '">'
                        data = data + '<img class="property-img" src="' + property_temp['data'][
                            'medium_square_crop'] + '" alt="' + field + '">'
                        data = data + '</a>'
                        return mark_safe(data)
                    else:
                        data = '<img src="' + property_temp.get('data') + '"alt="' + field + '">'
                        return mark_safe(data)
                else:
                    return mark_safe(property_temp.get('data'))
    return "-"


@register.simple_tag
def get_data_value(data, order):
    output = None
    if order == "first":
        output = data.get("first")
    elif order == "second":
        output = data.get("second")
    if data.get('type') == "list":
        data = ""
        for data_temp in output:
            data = data + data_temp + ", "
        return mark_safe(data[:-2])
    elif data.get('type') == "image":
        if type(output) is dict:
            image = '<a href="' + output.get('full_size') + '"'
            image = image + 'data-fancybox data-caption="' + data.get('name') + '">'
            image = image + '<img class="property-img" src="' + output.get('medium_square_crop') + '" alt="' + data.get(
                'name') + '">'
            image = image + '</a>'
            return mark_safe(image)
        else:
            data = '<img src="' + output + '"alt="' + data.get('name') + '">'
            return mark_safe(data)
    else:
        return mark_safe(output)


@register.simple_tag
def get_contents():
    return ContentType.objects.all()


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
