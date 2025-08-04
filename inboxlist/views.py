from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Count
from .models import InboxItem


def get_current_list(request):
    return request.COOKIES.get("list_name", "lokalna_lista")


def get_inbox_context(list_name):
    return {
        "unprocessed": InboxItem.objects.filter(
            list_name=list_name, is_processed=False
        ).order_by("-created_at"),
        "processed": InboxItem.objects.filter(
            list_name=list_name, is_processed=True
        ).order_by("-created_at"),
        "list_name": list_name,
    }


def inbox_entry_point(request):
    if not request.COOKIES.get("list_name"):
        return render(request, "inboxlist/select_list.html")
    return inbox_list(request)


def inbox_list(request):
    list_name = get_current_list(request)
    return render(request, "inboxlist/inbox.html", get_inbox_context(list_name))


@require_POST
def add_item(request):
    title = request.POST.get("title")
    list_name = get_current_list(request)
    if title:
        InboxItem.objects.create(title=title, list_name=list_name)
    items = InboxItem.objects.filter(list_name=list_name, is_processed=False).order_by(
        "-created_at"
    )
    return render(
        request,
        "inboxlist/partials/item_list.html",
        {"items": items, "processed": False, "list_name": list_name},
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
    list_name = get_current_list(request)
    item = get_object_or_404(InboxItem, pk=pk, list_name=list_name)
    item.is_processed = not item.is_processed
    item.save()
    return render(request, "inboxlist/inbox.html", get_inbox_context(list_name))


@require_POST
def delete_item(request, pk):
    list_name = get_current_list(request)
    item = get_object_or_404(InboxItem, pk=pk, list_name=list_name)
    item.delete()

    if request.headers.get("HX-Request"):
        return render(request, "inboxlist/inbox.html", get_inbox_context(list_name))

    return redirect("inbox_list")


def confirm_delete_modal(request, pk):
    item = get_object_or_404(InboxItem, pk=pk)
    html = render_to_string(
        "inboxlist/partials/confirm_delete_modal.html", {"item": item}, request=request
    )
    return HttpResponse(html)


def set_list(request):
    if request.method == "POST":
        list_name = request.POST.get("list_name", "").strip()
        if not list_name:
            return HttpResponse("Musisz podać nazwę listy.", status=400)
        response = HttpResponse(status=204)  # brak treści, HTMX wie że OK
        response.set_cookie("list_name", list_name, max_age=60 * 60 * 24 * 360)
        return response
    return HttpResponse("Błędna metoda", status=405)


def select_list(request):
    existing_lists = (
        InboxItem.objects.values("list_name")
        .annotate(item_count=Count("id"))
        .order_by("-item_count")
    )
    return render(
        request, "inboxlist/select_list.html", {"existing_lists": existing_lists}
    )
