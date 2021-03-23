from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.http import Http404
from turbo_response import redirect_303

from .models import TWordpress
from .forms import WordpressUploadForm


class TWordpressListView(ListView):

    model = TWordpress
    allow_empty = False

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect_303("wordpress:t_wordpress_create")


class TWordpressCreate(CreateView):
    form_class = WordpressUploadForm
    template_name = "wordpress/wordpress_create.html"
