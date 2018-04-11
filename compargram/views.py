from django.shortcuts import render
from app.thing.models import Compare
from django.http import HttpResponse


def welcome(request):
    new_compare = Compare.objects.all().order_by('-id')[:12]
    return render(request, 'welcome.html', {'comparison': new_compare})


def error_404(request):
    data = {}
    return render(request, 'error/404.html', data)


def error_500(request):
    data = {}
    return render(request, 'error/404.html', data)


def get_width(dict_data, width):
    if type(dict_data.get('data')) is list:
        if len(dict_data.get('data')) == 0:
            width = width + 1
        for temp in dict_data.get('data'):
            width = get_width(temp, width)
    return width


def test(request):
    dict_data = {
        "data": [
            {
                "data": [
                    {
                        "data": [
                            {
                                "data": [
                                    {
                                        "data": [

                                        ],
                                        "name": "Upholstery",
                                        "level": 3
                                    },
                                    {
                                        "data": [

                                        ],
                                        "name": "Bluetooth",
                                        "level": 3
                                    }
                                ],
                                "name": "Upholstery",
                                "level": 3
                            },
                            {
                                "data": [

                                ],
                                "name": "Bluetooth",
                                "level": 3
                            }
                        ],
                        "name": "Interior",
                        "first": {

                        },
                        "level": 2,
                        "second": {

                        }
                    }
                ],
                "name": "Car",
                "level": 1
            }
        ],
        "level": 0
    }
    return HttpResponse(get_width(dict_data, 0))
