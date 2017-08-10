from __future__ import unicode_literals

# TODO: Update the media_cdn folder everytime the name of the post is changed.
# TODO: Check if the image exists befor updating a post (maybe you deleted it while editing the post).
# TODO: Add something to style the post's content to make it look more readable and pro.
# TODO: Check the Breadcrumbs Bootstrap component

import datetime
import os
import uuid

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, pre_delete
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.
class PostManager(models.Manager):
    # vamos a sobreescribir managers que ya existen como por ejemplo: Posts.objects.all() o Posts.objects.create()
    # sobreescribiendo el fltro 'all', haremos que afecte a la vista 'detail' (post_detail) porque la queryset se hace a 'all', asi que mejor sobreescribimos el filtro 'active' que es el que considera publicaciones con fecha de hoy o anterior y que no es un draft
    #def all(self, *args, **kwargs):
    #    return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())
    def active(self, *args, **kwargs):
        return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())

# The upload_to can also be a callable that returns a string.
# This callable accepts two parameters, 'instance' and 'filename'.
def upload_location(instance, filename):
    return "%s/%s/%s" % (instance.slug, instance.id, filename)


class Post(models.Model):
    # Choices
    POST_TYPE = {
        ("P", "Personal"),
        ("T", "Topic"),
    }
    type = models.CharField(max_length=1, choices=POST_TYPE, default='T')
    # default=1 hace que el usuario por defecto para ese post sera el primer superusuario (ID = 1)
    # default=1 hara que todos los post ya creados que no tengan usuario, tomen un usuario cuando se hace migrations
    # TIP: siempre que trabajamos con una db ya creada y con datos, tenemos SIEMPRE que crear un 'default' para cada nuevo campo, asi no tenemos campos NULL en la db
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    titulo = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    # We need to use UUID field as primary key to have the instance of the object (Post) created in db by the time we want to call 'upload_location' to know what file to store and where.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # file will be uploaded to MEDIA_ROOT/upload_location (upload_location is a callable function to obtain the upload path, including the filename)
    # If the model field has blank=True, then required is set to False on the form field. Otherwise, required=True
    imagen = models.ImageField(upload_to=upload_location,
                               null=True,
                               blank=True,
                               height_field="height_field",
                               width_field="width_field")
    height_field = models.IntegerField(null=True, default=0)
    width_field = models.IntegerField(null=True, default=0)
    contenido = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False, default=datetime.date.today)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    actualizado = models.DateTimeField(auto_now_add=False, auto_now=True)

    # para asocial el modelo con el manager (al que hemos sobreescrito 'all')
    # 'objects' es el nombre default en django para nuestros objetos, lo podemos cambiar si quieremos, pero tenemos que cambiarlo tambien en el queryset den las vistas
    objects = PostManager()

    def __str__(self):
        return self.titulo

    # return reverse("posts:detail", kwargs={"id": self.id})
    def get_absolute_url(self):
        return reverse("posts:detail", kwargs={"slug":self.slug})

    # class Meta: To elements that are not related with the model's fields
    class Meta:
        # this could be done also in the views.py directly using: queryset = Post.objects.all().order_by("-timestamp")
        ordering = ["-timestamp", "-actualizado"]

# Para crear un slug pare cada post
# Esta funcion se ejecuta si no hay un slug para un post
def create_slug(instance, new_slug=None):
    slug = slugify(instance.titulo)
    if new_slug is not None:
        slug = new_slug
    # Miramos si ese slug es unico. Hemos dicho en la definicion que deben ser unicos
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

# funcion recursiva
def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, sender=Post)


def pre_delete_post_receiver(sender, instance, *args, **kwargs):
    if instance.imagen:
        instance.imagen.delete(False)

pre_delete.connect(pre_delete_post_receiver, sender=Post)


