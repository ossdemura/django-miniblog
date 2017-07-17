from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
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

def upload_location(instance, filename):
    return "%s/%s" % (instance.id, filename)


class Post(models.Model):
    # default=1 hace que el usuario por defecto para ese post sera el primer superusuario (ID = 1)
    # default=1 hara que todos los post ya creados que no tengan usuario, tomen un usuario cuando se hace migrations
    # TIP: siempre que trabajamos con una db ya creada y con datos, tenemos SIEMPRE que crear un 'default' para cada nuevo campo, asi no tenemos campos NULL en la db
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)

    titulo = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    imagen = models.ImageField(upload_to=upload_location,
                               null=True,
                               blank=True,
                               height_field="height_field",
                               width_field="width_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    contenido = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)
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
