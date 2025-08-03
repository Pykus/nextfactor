from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import InboxItem


def get_inbox_context():
    return {
        "unprocessed": InboxItem.objects.filter(is_processed=False).order_by(
            "-created_at"
        ),
        "processed": InboxItem.objects.filter(is_processed=True).order_by(
            "-created_at"
        ),
    }


def inbox_list(request):
    return render(request, "inboxlist/inbox.html", get_inbox_context())


@require_POST
def add_item(request):
    title = request.POST.get("title")
    if title:
        InboxItem.objects.create(title=title)
    items = InboxItem.objects.filter(is_processed=False).order_by("-created_at")
    return render(
        request,
        "inboxlist/partials/item_list.html",
        {"items": items, "processed": False},
    )


def edit_item(request, pk):
    item = get_object_or_404(InboxItem, pk=pk)
    return render(request, "inboxlist/partials/item_edit_form.html", {"item": item})


@require_POST
def update_item(request, pk):
    item = get_object_or_404(InboxItem, pk=pk)
    item.title = request.POST.get("title")
    item.save()
    return HttpResponse(item.title)


@require_POST
def toggle_processed(request, pk):
    item = get_object_or_404(InboxItem, pk=pk)
    item.is_processed = not item.is_processed
    item.save()
    return render(request, "inboxlist/inbox.html", get_inbox_context())


@require_POST
def delete_item(request, pk):
    item = get_object_or_404(InboxItem, pk=pk)
    item.delete()

    if request.headers.get("HX-Request"):
        return render(request, "inboxlist/inbox.html", get_inbox_context())

    return redirect("inbox_list")


def confirm_delete_modal(request, pk):
    item = get_object_or_404(InboxItem, pk=pk)
    html = render_to_string(
        "inboxlist/partials/confirm_delete_modal.html", {"item": item}, request=request
    )
    return HttpResponse(html)
