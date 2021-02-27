from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, FormView
from indieweb.constants import MPostStatuses, MPostKinds
from indieweb.webmentions import send_webmention
from indieweb.extract import extract_reply_details_from_url
from post.models import MPostKind
from turbo_response import TurboFrame
from turbo_response import TurboStreamResponse, TurboStream


from . import forms, models


@method_decorator(login_required, name="dispatch")
class CreateEntryView(CreateView):
    autofocus = None
    redirect_url = "status_edit"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"p_author": self.request.user, "autofocus": self.autofocus})
        return kwargs

    def form_valid(self, form):
        form.prepare_data()
        entry = form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, entry.t_post, entry.e_content)

        permalink_a_tag = render_to_string(
            "fragments/view_post_link.html", {"t_post": entry.t_post}
        )
        messages.success(
            self.request,
            f"Saved {form.cleaned_data['m_post_kind']}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(resolve_url(self.redirect_url, pk=entry.pk))

    def form_invalid(self, form):
        context = {"form": form, "nav": "posts"}
        return render(self.request, self.template_name, context=context, status=422)


@method_decorator(login_required, name="dispatch")
class UpdateEntryView(UpdateView):
    m_post_kind = None
    original_content = ""

    def get_queryset(self):
        return models.TEntry.objects.select_related("t_post").filter(
            t_post__m_post_kind__key=self.m_post_kind
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self.original_content = obj.e_content
        return obj

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["nav"] = "posts"
        return context_data

    def form_valid(self, form):
        form.prepare_data()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, form.instance.t_post, self.original_content)

        form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, form.instance.t_post, form.instance.e_content)

        permalink_a_tag = render_to_string(
            "fragments/view_post_link.html", {"t_post": form.instance.t_post}
        )
        messages.success(
            self.request,
            f"Saved {form.instance.t_post.m_post_kind.key}. {mark_safe(permalink_a_tag)}",
        )
        context = self.get_context_data(form=form)
        return self.get_response(context)

    def get_response(self, context):
        return render(self.request, self.template_name, context=context)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context=context)


# Note CRUD views


class CreateStatusView(CreateEntryView):
    form_class = forms.CreateStatusForm
    template_name = "entry/note/create.html"


class UpdateStatusView(UpdateEntryView):
    form_class = forms.UpdateStatusForm
    template_name = "entry/note/update.html"
    m_post_kind = MPostKinds.note


# Article CRUD views


class CreateArticleView(CreateEntryView):
    form_class = forms.CreateArticleForm
    template_name = "entry/article/create.html"
    autofocus = "p_name"
    redirect_url = "article_edit"


class UpdateArticleView(UpdateEntryView):
    form_class = forms.UpdateArticleForm
    template_name = "entry/article/update.html"
    m_post_kind = MPostKinds.article
    autofocus = "p_name"


# Reply CRUD views


class CreateReplyView(CreateEntryView):
    template_name = "entry/reply/create.html"
    redirect_url = "reply_edit"

    def get_context_data(self, **kwargs):
        return super().get_context_data(nav="posts", **kwargs)

    def get_form_class(self):
        if self.request.method == "GET":
            return forms.ExtractMetaForm
        return forms.CreateReplyForm

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return (
            TurboFrame("reply-form")
            .template("entry/reply/form.html", context)
            .response(self.request)
        )


@method_decorator(login_required, name="dispatch")
class ExtractReplyMetaView(FormView):
    form_class = forms.ExtractMetaForm

    def get_context_data(self, **kwargs):
        return super().get_context_data(nav="posts", **kwargs)

    def form_valid(self, form):
        linked_page = extract_reply_details_from_url(form.cleaned_data["url"])
        initial = {
            "u_in_reply_to": linked_page.url,
            "title": linked_page.title,
            "author": linked_page.author.name,
            "summary": linked_page.description,
        }
        context = self.get_context_data(
            form=forms.CreateReplyForm(initial=initial, p_author=self.request.user),
        )

        return (
            TurboFrame("reply-form")
            .template("entry/reply/form.html", context)
            .response(self.request)
        )

    def form_invalid(self, form):
        return render(
            self.request,
            "entry/reply/_url_form.html",
            context=self.get_context_data(),
            status=422,
        )


class UpdateReplyView(UpdateEntryView):
    form_class = forms.UpdateReplyForm
    template_name = "entry/reply/update.html"
    m_post_kind = MPostKinds.reply
    autofocus = "e_content"

    def get_response(self, context):
        return (
            TurboFrame("messages")
                .template("fragments/messages.html", context)
                .response(self.request)
        )


@login_required
def status_detail(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related("t_post"), pk=pk)
    context = {"status": status, "nav": "posts"}
    return render(request, "entry/status_detail.html", context=context)


@login_required
def status_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Status Deleted")
    return redirect(resolve_url("posts"))


@method_decorator(login_required, name="dispatch")
class TEntryListView(ListView):
    template_name = "entry/posts.html"
    m_post_kind_key = None
    m_post_kind = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.m_post_kind_key:
            self.m_post_kind = get_object_or_404(MPostKind, key=self.m_post_kind_key)

    def get_queryset(self):
        qs = models.TEntry.objects.all()
        if self.m_post_kind:
            qs = qs.filter(t_post__m_post_kind=self.m_post_kind)
        return qs.order_by("-created_at")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["nav"] = "posts"
        return context


@login_required
def article_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Article Deleted")
    return redirect(resolve_url("posts"))


@login_required
def edit_post(request, pk: int):
    t_entry = get_object_or_404(
        models.TEntry.objects.select_related("t_post", "t_post__m_post_kind"), pk=pk
    )
    if t_entry.t_post.m_post_kind.key == MPostKinds.article:
        return redirect(reverse("article_edit", args=[pk]))
    elif t_entry.t_post.m_post_kind.key == MPostKinds.note:
        return redirect(reverse("status_edit", args=[pk]))
    elif t_entry.t_post.m_post_kind.key == MPostKinds.reply:
        return redirect(reverse("reply_edit", args=[pk]))
    messages.error(request, "Unknown post type")
    return redirect(resolve_url("posts"))
