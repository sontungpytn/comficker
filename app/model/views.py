# coding: utf-8
import itertools
import json
from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.forms import models as model_forms
from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.utils.text import slugify
from django.core.urlresolvers import reverse_lazy


class GenericModelView(View):
    """
    Base class for all model generic views.
    """
    model = None
    fields = None
    vote_model = None
    review_model = None
    field_mode = None
    classify = None
    # Object lookup parameters. These are used in the URL kwargs, and when
    # performing the model instance lookup.
    # Note that if unset then `lookup_url_kwarg` defaults to using the same
    # value as `lookup_field`.
    lookup_field = 'pk'
    lookup_url_kwarg = None

    # All the following are optional, and fall back to default values
    # based on the 'model' shortcut.
    # Each of these has a corresponding `.get_<attribute>()` method.
    queryset = None
    form_class = None
    template_name = None
    context_object_name = None

    # Pagination parameters.
    # Set `paginate_by` to an integer value to turn pagination on.
    paginate_by = None
    page_kwarg = 'page'

    #  Suffix that should be appended to automatically generated template names.
    template_name_suffix = None

    # Queryset and object lookup

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        try:
            lookup = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        except KeyError:
            msg = "Lookup field '%s' was not provided in view kwargs to '%s'"
            raise ImproperlyConfigured(msg % (lookup_url_kwarg, self.__class__.__name__))

        return get_object_or_404(queryset, **lookup)

    def get_queryset(self):
        """
        Returns the base queryset for the view.

        Either used as a list of objects to display, or as the queryset
        from which to perform the individual object lookup.
        """
        if self.queryset is not None:
            return self.queryset._clone()

        if self.model is not None:
            return self.model._default_manager.all()

        msg = "'%s' must either define 'queryset' or 'model', or override 'get_queryset()'"
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    # Form instantiation

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class is not None:
            return self.form_class

        if self.model is not None and self.fields is not None:
            return model_forms.modelform_factory(self.model, fields=self.fields)

        msg = "'%s' must either define 'form_class' or both 'model' and " \
              "'fields', or override 'get_form_class()'"
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_form(self, data=None, files=None, **kwargs):
        """
        Returns a form instance.
        """
        cls = self.get_form_class()
        return cls(data=data, files=files, **kwargs)

    # Pagination

    def get_paginate_by(self):
        """
        Returns the size of pages to use with pagination.
        """
        return self.paginate_by

    def get_paginator(self, queryset, page_size):
        """
        Returns a paginator instance.
        """
        return Paginator(queryset, page_size)

    def paginate_queryset(self, queryset, page_size):
        """
        Paginates a queryset, and returns a page object.
        """
        paginator = self.get_paginator(queryset, page_size)
        page_kwarg = self.kwargs.get(self.page_kwarg)
        page_query_param = self.request.GET.get(self.page_kwarg)
        page_number = page_kwarg or page_query_param or 1
        try:
            page_number = int(page_number)
        except ValueError:
            if page_number == 'last':
                page_number = paginator.num_pages
            else:
                msg = "Page is not 'last', nor can it be converted to an int."
                raise Http404(_(msg))

        try:
            return paginator.page(page_number)
        except InvalidPage as exc:
            msg = 'Invalid page (%s): %s'
            raise Http404(_(msg % (page_number, str(exc))))

    # Response rendering

    def get_context_object_name(self, is_list=False):
        """
        Returns a descriptive name to use in the context in addition to the
        default 'object'/'object_list'.
        """
        if self.context_object_name is not None:
            return self.context_object_name

        elif self.model is not None:
            fmt = '%s_list' if is_list else '%s'
            return fmt % self.model._meta.object_name.lower()

        return None

    def get_app_name(self):
        return self.model._meta.app_label.replace('model_', '')

    def get_context_data(self, **kwargs):
        """
        Returns a dictionary to use as the context of the response.

        Takes a set of keyword arguments to use as the base context,
        and adds the following keys:

        * 'view'
        * Optionally, 'object' or 'object_list'
        * Optionally, '{context_object_name}' or '{context_object_name}_list'
        """
        kwargs['view'] = self

        if getattr(self, 'object', None) is not None:
            kwargs['model'] = self.object
            kwargs['name'] = self.get_app_name

        if getattr(self, 'object_list', None) is not None:
            kwargs['object_list'] = self.object_list
            context_object_name = self.get_context_object_name(is_list=True)
            if context_object_name:
                kwargs[context_object_name] = self.object_list

        return kwargs

    def get_template_names(self):
        """
        Returns a list of template names to use when rendering the response.

        If `.template_name` is not specified, then defaults to the following
        pattern: "{app_label}/{model_name}{template_name_suffix}.html"
        """
        if self.template_name is not None:
            return [self.template_name]

        if self.model is not None and self.template_name_suffix is not None:
            return ["%s/%s%s.html" % (
                self.model._meta.app_label,
                self.model._meta.object_name.lower(),
                self.template_name_suffix
            )]

        msg = "'%s' must either define 'template_name' or 'model' and " \
              "'template_name_suffix', or override 'get_template_names()'"
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def render_to_response(self, context):
        """
        Given a context dictionary, returns an HTTP response.
        """
        return TemplateResponse(
            request=self.request,
            template=self.get_template_names(),
            context=context
        )


# The concrete model views


class ListView(GenericModelView):
    template_name_suffix = '_list'
    template_name = 'index.html'
    allow_empty = True

    def get(self, request, *args, **kwargs):
        classifies = self.classify.objects.all()
        queryset = self.get_queryset()
        paginate_by = self.get_paginate_by()
        if not self.allow_empty and not queryset.exists():
            raise Http404

        if paginate_by is None:
            #  Unpaginated response
            self.object_list = queryset
            context = self.get_context_data(
                page_obj=None,
                is_paginated=False,
                paginator=None,
            )
        else:
            # Paginated response
            page = self.paginate_queryset(queryset, paginate_by)
            self.object_list = page.object_list
            context = self.get_context_data(
                page_obj=page,
                is_paginated=page.has_other_pages(),
                paginator=page.paginator,
            )
        context['classifies'] = classifies
        context['name'] = self.get_app_name
        return self.render_to_response(context)


class DetailView(GenericModelView):
    template_name_suffix = '_detail'
    lookup_url_kwarg = 'model_slug'
    lookup_field = 'slug'
    template_name = 'model/model_show.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        list_field = self.field_mode.objects.all()
        context['fields'] = list_field
        context['classes'] = self.object.classifies()
        return self.render_to_response(context)


class CreateView(GenericModelView):
    success_url = None
    template_name = 'model/model_create.html'
    template_name_suffix = '_form'

    def get(self, request, *args, **kwargs):
        context = {'name': self.get_app_name}
        if not request.user.is_authenticated:
            return HttpResponse("Login please!")
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("Login please!")
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        try:
            return self.success_url or self.object.get_absolute_url()
        except AttributeError:
            msg = "No URL to redirect to. '%s' must provide 'success_url' " \
                  "or define a 'get_absolute_url()' method on the Model."
            raise ImproperlyConfigured(msg % self.__class__.__name__)


class UpdateView(GenericModelView):
    success_url = None
    template_name_suffix = '_form'
    lookup_url_kwarg = 'model_slug'
    lookup_field = 'slug'
    template_name = 'model/model_edit.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.id != self.object.user.id:
            return HttpResponse("Login please!")
        context = self.get_context_data()
        context['name'] = self.get_app_name
        return self.render_to_response(context)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        try:
            return self.success_url or self.object.get_absolute_url()
        except AttributeError:
            msg = "No URL to redirect to. '%s' must provide 'success_url' " \
                  "or define a 'get_absolute_url()' method on the Model."
            raise ImproperlyConfigured(msg % self.__class__.__name__)


class DeleteView(GenericModelView):
    lookup_url_kwarg = 'model_slug'
    lookup_field = 'slug'
    template_name = 'model/model_delete.html'
    template_name_suffix = '_done'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.id != self.object.user.id:
            return HttpResponse("Login please!")
        context = self.get_context_data()
        context['name'] = self.get_app_name
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.id != self.object.user.id:
            return HttpResponse("Login please!")
        self.object.delete()
        strix = self.get_app_name() + ':' + self.get_app_name() + '_index'
        return HttpResponseRedirect(reverse_lazy(strix))

    def get_success_url(self):
        if self.success_url is None:
            msg = "No URL to redirect to. '%s' must define 'success_url'"
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        return self.success_url


class VoteView(GenericModelView):
    success_url = None

    def get(self, request, *args, **kwargs):
        result = {}
        liked = False
        model = get_object_or_404(self.model, slug=kwargs['model_slug'])
        count = self.vote_model.objects.filter(model=model).count()
        if request.user.is_authenticated:
            like_obj = self.vote_model.objects.filter(model=model, user=request.user).first()
            if like_obj is not None:
                liked = True
        result['count'] = count
        result['liked'] = liked
        return HttpResponse(json.dumps(result))

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            model = get_object_or_404(self.model, slug=kwargs['model_slug'])
            vote_obj = self.vote_model.objects.filter(model=model, user=request.user).first()
            if vote_obj is None:
                vote_obj = self.vote_model()
                vote_obj.model = model
                vote_obj.user = request.user
                vote_obj.pub_date = timezone.now()
                vote_obj.save()
                return HttpResponse("LIKED")
            else:
                vote_obj.delete()
                return HttpResponse("UNLIKED")
        else:
            return HttpResponse("You must to login first!")


class ClassifyView(GenericModelView):
    template_name_suffix = '_list'
    template_name = 'model/model_classify.html'
    allow_empty = True

    def get(self, request, *args, **kwargs):
        classifies = self.classify.objects.all()
        list_field = self.field_mode.objects.all()
        context = {}
        context['classifies'] = classifies
        context['fields'] = list_field
        context['name'] = self.get_app_name
        return self.render_to_response(context)


class FieldView(GenericModelView):
    template_name = 'model/model_field.html'

    def get(self, request, *args, **kwargs):
        field_value = []
        context = {}
        if kwargs['field'] == "category":
            context['classify_name'] = "Category"
            classifies = self.classify.objects.all()
            for classify in classifies:
                field_value.append(classify.name)
        else:
            models = self.model.objects.all()
            for model in models:
                for property_temp in model.properties:
                    if property_temp.get('type') == "list" and slugify(property_temp.get('name')) == kwargs['field']:
                        for data in property_temp.get('data'):
                            field_value.append(data)
                            context['classify_name'] = property_temp.get('name')
                    elif property_temp.get('type') == "tag" and slugify(property_temp.get('name')) == kwargs['field']:
                        field_value.append(property_temp.get('data'))
                        context['classify_name'] = property_temp.get('name')
        context['object_list'] = set(field_value)
        context['name'] = self.get_app_name
        return self.render_to_response(context)


class FilterView(GenericModelView):
    template_name = 'search.html'

    def get(self, request, *args, **kwargs):
        object_list = []
        context = {}
        if kwargs['field'] == "category":
            models = self.model.objects.all()
            for model in models:
                for classify in model.classifies():
                    if slugify(kwargs['value']) == slugify(classify):
                        object_list.append(model)
                        context['classify_value'] = classify
            context['classify_name'] = "Category"
        else:
            models = self.model.objects.all()
            for model in models:
                for property_temp in model.properties:
                    if property_temp.get('type') == "list" and slugify(property_temp.get('name')) == kwargs['field']:
                        for data in property_temp.get('data'):
                            if data.replace(" ", "-") == kwargs['value']:
                                object_list.append(model)
                                context['classify_value'] = data
                                context['classify_name'] = property_temp.get('name')
                    elif property_temp.get('type') == "tag" and slugify(property_temp.get('name')) == kwargs['field']:
                        if property_temp.get('data').replace(" ", "-") == kwargs['value']:
                            object_list.append(model)
                            context['classify_value'] = property_temp.get('data')
                            context['classify_name'] = property_temp.get('name')
        context['object_list'] = set(object_list)
        context['name'] = self.get_app_name
        return self.render_to_response(context)


class CompareClassify(GenericModelView):
    template_name_suffix = '_list'
    template_name = 'model/compare_classify.html'
    allow_empty = True

    def get(self, request, *args, **kwargs):
        classifies = self.classify.objects.exclude(parent=None).order_by('name')
        if not self.allow_empty and not classifies.exists():
            raise Http404
        data = list(itertools.combinations_with_replacement(classifies, 2))
        paginator = Paginator(data, 9)
        page = request.GET.get('page')
        try:
            list_compare = paginator.page(page)
        except PageNotAnInteger:
            list_compare = paginator.page(1)
        except EmptyPage:
            list_compare = paginator.page(paginator.num_pages)
        context = {}
        context['test'] = list_compare
        context['name'] = self.get_app_name
        return self.render_to_response(context)


class CompareList(GenericModelView):
    template_name = 'model/compare_list.html'
    allow_empty = True

    def get(self, request, *args, **kwargs):
        models = self.get_queryset().order_by('name')
        context = {}
        queryset = []
        data = []
        context['first'] = None
        context['second'] = None
        if kwargs['first'] == kwargs['second']:
            for model in models:
                for classify in model.classifies():
                    if slugify(classify) == kwargs['first']:
                        queryset.append(model)
                        if context['first'] is None or context['second'] is None:
                            context['first'] = classify
                            context['second'] = classify
            data = list(itertools.combinations(queryset, 2))
        else:
            first = []
            second = []
            for model in models:
                for classify in model.classifies():
                    if slugify(classify) == kwargs['first']:
                        first.append(model)
                        if context['first'] is None:
                            context['first'] = classify
                    if slugify(classify) == kwargs['second']:
                        second.append(model)
                        if context['second'] is None:
                            context['second'] = classify
            for elm1 in first:
                for elm2 in second:
                    if elm1.name < elm2.name:
                        data.append([elm1, elm2])
                    else:
                        data.append([elm2, elm1])
        paginator = Paginator(data, 9)
        page = request.GET.get('page')
        try:
            list_compare = paginator.page(page)
        except PageNotAnInteger:
            list_compare = paginator.page(1)
        except EmptyPage:
            list_compare = paginator.page(paginator.num_pages)
        context['test'] = list_compare
        context['name'] = self.get_app_name
        return self.render_to_response(context)


class CompareDetail(GenericModelView):
    template_name = 'model/compare_detail.html'

    def get(self, request, *args, **kwargs):
        context_object_name = self.get_app_name()
        queryset = self.get_queryset()
        first = get_object_or_404(queryset, slug=kwargs['first'])
        second = get_object_or_404(queryset, slug=kwargs['second'])
        if kwargs['first'] < kwargs['second']:
            reviews = self.review_model.objects.filter(first=first, second=second)
            list_class = first.classifies().union(second.classifies())
            list_field = self.field_mode.objects.all()
            context = {}
            context['name'] = self.get_app_name
            context['first'] = first
            context['second'] = second
            context['reviews'] = reviews
            context['fields'] = list_field
            context['classes'] = list_class
            return self.render_to_response(context)
        elif kwargs['first'] == kwargs['second']:
            return HttpResponseRedirect('/' + context_object_name + '/' + kwargs['second'])
        else:
            return HttpResponseRedirect('/' + context_object_name + '/' + kwargs['second'] + '-and-' + kwargs['first'])

    def post(self, request, *args, **kwargs):
        context_object_name = self.get_app_name()
        if request.POST['submit'] == 'edit':
            review_object = self.review_model.objects.get(pk=request.POST['review_id'])
            if request.user.id != review_object.user.id:
                return HttpResponse("Login please!")
            review_object.title = request.POST['review_title']
            review_object.content = request.POST['review_content']
            review_object.save()
            return HttpResponseRedirect('/' + context_object_name + '/' + kwargs['first'] + '-and-' + kwargs['second'])
        elif request.POST['submit'] == 'delete':
            review_object = self.review_model.objects.get(pk=request.POST['review_id'])
            if request.user.id != review_object.user.id:
                return HttpResponse("Login please!")
            review_object.delete()
            return HttpResponseRedirect('/' + context_object_name + '/' + kwargs['first'] + '-and-' + kwargs['second'])
        else:
            queryset = self.get_queryset()
            first = get_object_or_404(queryset, slug=kwargs['first'])
            second = get_object_or_404(queryset, slug=kwargs['second'])
            review_object = self.review_model()
            review_object.title = request.POST['review_title']
            review_object.content = request.POST['review_content']
            review_object.first = first
            review_object.second = second
            review_object.user = request.user
            review_object.save()
            return HttpResponseRedirect('/' + context_object_name + '/' + kwargs['first'] + '-and-' + kwargs['second'])
