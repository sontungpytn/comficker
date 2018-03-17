from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import slugify
from .models import Image, Gallery, GalleryRelationship
from .models import decode_base64_file
from .form import ImageForm


def media_index(request):
    gallery = Gallery.objects.all()
    paginator = Paginator(gallery, 8)
    page = request.GET.get('page')
    try:
        galleries = paginator.page(page)
    except PageNotAnInteger:
        galleries = paginator.page(1)
    except EmptyPage:
        galleries = paginator.page(paginator.num_pages)
    return render(request, 'media_index.html', {'galleries': galleries})


def media_all(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        list_images = paginator.page(page)
    except PageNotAnInteger:
        list_images = paginator.page(1)
    except EmptyPage:
        list_images = paginator.page(paginator.num_pages)
    return render(request, 'media/media_index.html', {'images': list_images})


def media_show(request, id):
    image = Image.objects.filter(pk=id).first()
    return render(request, 'media/media_show.html', {'image': image})


def media_upload(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                image = Image()
                image.title = form.cleaned_data['title']
                prefix = slugify(form.cleaned_data['title']) + "_"
                image.description = form.cleaned_data['description']
                image.user_id = request.user.id
                image.path = decode_base64_file(request.POST['file'], prefix)
                image.pub_date = timezone.now()
                image.save()
                return HttpResponse(image.id)
        else:
            form = ImageForm()
        return render(request, 'media/media_upload.html', {
            'form': form
        })
    else:
        message = "You must to login first!"
        return render(request, 'error/error.html', {'message': message})


def media_edit(request, id):
    image = Image.objects.filter(pk=id).first()
    if request.user.is_authenticated and image.user.id == request.user.id:
        if request.method == 'POST':
            form = ImageForm(request.POST, instance=image)
            if form.is_valid():
                form.save()
                return redirect('media:show_media', image.id)
            else:
                return render(request, 'media/media_edit.html', {
                    'form': form,
                    'image': image
                })
        else:
            form = ImageForm(instance=image)
            return render(request, 'media/media_edit.html', {
                'form': form,
                'image': image
            })
    else:
        message = "You can't edit this photo!"
        return render(request, 'error/error.html', {
            'message': message
        })


def media_delete(request, id):
    image = Image.objects.filter(pk=id).get()

    if request.user.is_authenticated and image.user.id == request.user.id:
        if request.method == 'POST':
            gallery = Gallery.objects.filter(featured=image).first()
            if gallery is not None:
                relation = GalleryRelationship.objects.filter(image=image, gallery=gallery).first()
                if relation is not None:
                    relation.delete()
                new_relation = GalleryRelationship.objects.filter(gallery=gallery).first()
                if new_relation is None:
                    gallery.delete()
                else:
                    gallery.featured = new_relation.image
                    gallery.save()
            image.path.delete_sized_images()
            image.delete()
            return redirect('/media/all')
        else:
            return render(request, 'media/confirm_delete.html', {'model': image})
    else:
        message = "You can't edit this photo!"
        return render(request, 'error/error.html', {
            'message': message
        })


def gallery_index(request):
    galleries = Gallery.objects.all()
    paginator = Paginator(galleries, 7)
    page = request.GET.get('page')
    try:
        list_galleries = paginator.page(page)
    except PageNotAnInteger:
        list_galleries = paginator.page(1)
    except EmptyPage:
        list_galleries = paginator.page(paginator.num_pages)
    return render(request, 'gallery/index.html', {'galleries': list_galleries})


def gallery_add(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            return
        else:
            return render(request, 'gallery/create.html')
    else:
        message = "You must to login first!"
        return render(request, 'error/error.html', {
            'message': message
        })


def gallery_show(request, slug):
    gallery = Gallery.objects.filter(slug=slug).first()
    if gallery is None:
        message = "You must to login first!"
        return render(request, 'error/error.html', {'message': message})
    photos = GalleryRelationship.objects.filter(gallery=gallery)
    return render(request, 'gallery/show.html', {'gallery': gallery, 'photos': photos})


def gallery_edit(request, slug):
    gallery = Gallery.objects.filter(slug=slug).get()
    if request.user.is_authenticated and gallery.user.id == request.user.id:
        return render(request, 'gallery/edit.html', {'gallery': gallery})
    else:
        message = "You must to login first!"
        return render(request, 'error/error.html', {'message': message})


def gallery_delete(request, slug):
    gallery = Gallery.objects.filter(slug=slug).get()
    if request.user.is_authenticated and gallery.user.id == request.user.id:
        if request.method == 'POST':
            gallery.delete()
            return redirect('/media/gallery')
        else:
            return render(request, 'media/confirm_delete.html', {'model': gallery})
    else:
        message = "You can't delete this gallery!"
        return render(request, 'error/error.html', {
            'message': message
        })


