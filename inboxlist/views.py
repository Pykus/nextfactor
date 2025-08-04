from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Count
from .models import InboxItem


def get_db_for_list(list_name: str) -> str:
    return "local_list" if list_name == "lokalna_lista" else "default"


def get_current_list(request):
    return request.COOKIES.get("list_name", "lokalna_lista")


def get_inbox_context(list_name):
    return {
        "unprocessed": InboxItem.objects.using(get_db_for_list(list_name))
        .filter(list_name=list_name, is_processed=False)
        .order_by("-created_at"),
        "processed": InboxItem.objects.using(get_db_for_list(list_name))
        .filter(list_name=list_name, is_processed=True)
        .order_by("-created_at"),
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
    db = get_db_for_list(list_name)
    if title:
        InboxItem.objects.using(db).create(title=title, list_name=list_name)
    items = (
        InboxItem.objects.using(db)
        .filter(list_name=list_name, is_processed=False)
        .order_by("-created_at")
    )
    return render(
        request,
        "inboxlist/partials/item_list.html",
        {"items": items, "processed": False, "list_name": list_name},
    )


def edit_item(request, pk):
    db = get_db_for_list(get_current_list(request))
    item = get_object_or_404(InboxItem.objects.using(db), pk=pk)
    return render(request, "inboxlist/partials/item_edit_form.html", {"item": item})


@require_POST
def update_item(request, pk):
    db = get_db_for_list(get_current_list(request))
    item = get_object_or_404(InboxItem.objects.using(db), pk=pk)
    item.title = request.POST.get("title")
    item.save()
    return HttpResponse(item.title)


@require_POST
def toggle_processed(request, pk):
    list_name = get_current_list(request)
    db = get_db_for_list(list_name)
    item = get_object_or_404(InboxItem.objects.using(db), pk=pk, list_name=list_name)
    item.is_processed = not item.is_processed
    item.save()
    return render(request, "inboxlist/inbox.html", get_inbox_context(list_name))


@require_POST
def delete_item(request, pk):
    list_name = get_current_list(request)
    db = get_db_for_list(list_name)
    item = get_object_or_404(InboxItem.objects.using(db), pk=pk, list_name=list_name)
    item.delete()

    if request.headers.get("HX-Request"):
        return render(request, "inboxlist/inbox.html", get_inbox_context(list_name))

    return redirect("inbox_list")


def confirm_delete_modal(request, pk):
    db = get_db_for_list(get_current_list(request))
    item = get_object_or_404(InboxItem.objects.using(db), pk=pk)
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
    all_lists = []

    # z default (czyli zdalnej/postgres)
    remote_lists = (
        InboxItem.objects.using("default")
        .values("list_name")
        .annotate(item_count=Count("id"))
    )
    all_lists.extend(remote_lists)

    # z lokalnej bazy
    local_lists = (
        InboxItem.objects.using("local_list")
        .values("list_name")
        .annotate(item_count=Count("id"))
    )
    all_lists.extend(local_lists)

    # posortuj malejąco po liczbie elementów
    sorted_lists = sorted(all_lists, key=lambda x: -x["item_count"])

    return render(
        request, "inboxlist/select_list.html", {"existing_lists": sorted_lists}
    )
