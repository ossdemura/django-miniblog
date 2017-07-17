from django.conf.urls import include, url
from . import views 

# Utilizar paréntesis en torno a un patrón "captura" el texto buscado por ese patrón
# y lo envía como un argumento a la función de vista. En la vista, como parametro de entrada
# del metodo post_detail, podremos usar 'id' porque forma parte del patron r'^(?P<id>\d+)/$,
# def post_detail(request, id)

urlpatterns = [
    url(r'^$', views.post_list, name='list'),
    url(r'^create/$', views.post_create),
    url(r'^(?P<id>\d+)/$', views.post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/$', views.post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', views.post_delete),

]