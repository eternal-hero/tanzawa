from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.contrib import messages

from . import forms
from . import models


def status_create(request):
    form = forms.CreateArticleForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            entry = form.save()
            # todo: add some turoframe jazz
            form = forms.CreateArticleForm()
            messages.success(request, "Saved Status")
    # messages.success(request, "Saved Status")
    context = {
        'form': form
    }
    return render(request, "entry/status_create.html", context=context)


def status_edit(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related('t_post'), pk=pk)

    form = forms.UpdateArticleForm(request.POST or None, instance=status)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            form.save()
            messages.success(request, "Saved Status")
    context = {
        'form': form

    }
    return render(request, "entry/status_update.html", context=context)


def status_detail(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related('t_post'), pk=pk)
    context = {
        'status': status

    }
    return render(request, "entry/status_detail.html", context=context)


def status_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related('t_post'), pk=pk)
    status.delete()
    messages.success(request, "Status Deleted")
    return redirect(resolve_url("status_list"))


def status_list(request):
    objects = models.TEntry.objects.all()
    return render(request, "entry/status_list.html", context={"objects": objects})
