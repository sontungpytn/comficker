from django import template
from django.apps import apps
from django.utils.safestring import mark_safe

from app.general.models import ContentType
from app.general.models import Definition

register = template.Library()


@register.filter(is_safe=True)
def half_slug(value):
    return value.replace(" ", "-")


@register.simple_tag
def get_gallery(customer, classify_name):
    models = apps.get_model(app_label='model_' + customer, model_name='model').objects.all()
    for model in models:
        for classify in model.classifies():
            if classify_name == classify.name:
                return model.gallery.featured.path.crop['400x400']
    return None


@register.simple_tag
def get_define(name):
    define = Definition.objects.filter(name=name).first()
    if define is None:
        return name
    else:
        data = '<span data-tooltip aria-haspopup="true" class="has-tip top" data-disable-hover="false" tabindex="2" ' \
               'title="' + define.content + '">' + name + '</span>'
        return mark_safe(data)


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
def get_contents():
    return ContentType.objects.all()


@register.simple_tag
def get_meta_description(fields):
    data_temp = []
    for field in fields:
        data_temp.append(field.name)
    data = ", ".join(data_temp)
    return mark_safe(data)