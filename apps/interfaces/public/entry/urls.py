from django.urls import path

from . import views

urlpatterns = [
    path("<uuid:uuid>", views.status_detail, name="post_detail"),
    path("bookmarks/", views.Bookmarks.as_view(), name="bookmarks"),
]
