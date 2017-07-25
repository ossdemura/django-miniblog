from urllib.parse import quote
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import PostForm
from .models import Post


# Create your views here.
def post_create(request):
    # control de acceso para usuarios que no son del staff o no es el superusuario
    # if not request.user.is_staff or not request.user.is_superuser:
    if not request.user.is_authenticated():
        raise Http404

    form = PostForm(request.POST or None, request.FILES or None)

    # if request.method == "POST":
    #     print(request.POST.get("titulo"))
    #     print(request.POST.get("contenido"))

    if form.is_valid():
        instance = form.save(commit=False)
        # print(form.cleaned_data.get("titulo"))
        # instance.user funciona porque suponemos que hay una sesion abierta para un usuario, sino no llegarismoa a esta linea porque tenemos mas arriba el if para comprobar que somos usuario autenticado
        instance.user = request.user
        instance.save()
        messages.success(request, "Post creado con exito!")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form
    }
    return render(request, "post_form.html", context)


def post_detail(request, slug=None):
    # instance = Post.objects.get(id=1)
    instance = get_object_or_404(Post, slug=slug)
    # no queremos que usuarios que no son superusers vean drafts
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    share_string = quote(instance.titulo)
    context = {
        "titulo": instance.titulo,
        "instance": instance,
        "share_string": share_string,
    }
    return render(request, "post_detail.html", context)


def post_list(request):
    today = timezone.now().date()
    # en la lista no queremos ver: BORRADORES, POSTS CON FECHA FUTURO si no somos superusers o parte del staff
    # publish_lte =  publish less than (<)
    #queryset_list = Post.objects.filter(publish__lte=timezone.now()).filter(draft=False)
    #queryset_list = Post.objects.all() #.order_by("-timestamp")
    queryset_list = Post.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()

    # para hacer que el buscador en nuestra lista funcione, modificando el queryset con lo que el user ha escrito
    # usarmos Q para poder aplicar mas de un criterio para filtrar
    # 'distinct' se usa para no tener posts duplicados
    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(titulo__icontains=query)|
            Q(contenido__icontains=query)|
            Q(user__first_name__icontains=query)|
            Q(user__last_name__icontains=query)
            ).distinct()

    paginator = Paginator(queryset_list, 2)  # Show 2 contacts per page

    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        "titulo": "List",
        "object_list": queryset,
        "today": today,
    }

    return render(request, "post_list.html", context)


def post_update(request, slug=None):
    # control de acceso para usuarios que no son del staff o no es el superusuario
    if not request.user.is_authenticated():
        raise Http404

    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "The <a href='#'>post</a> has been updated", extra_tags='html_safe')
        # messages.success(request, "2do mensaje para el update del <a href='#'>post</a> - sin tag 'html_safe'", extra_tags='otro-tag')
        # messages.success(request, "3er mensaje para el update del <a href='#'>post</a> - sin tag 'html_safe'")

        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "titulo": instance.titulo,
        "instance": instance,
        "form": form
    }
    return render(request, "post_form.html", context)


def post_delete(request, slug=None):
    # control de acceso para usuarios que no son del staff o no es el superusuario
    if not request.user.is_authenticated():
        raise Http404

    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "El post ha sido eliminado")
    return redirect("posts:list")

