from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse

from .models import Authority, AuthorityType, Museum
from .forms import AuthorityForm, MuseumForm


# إضافة هيئة جديدة
def add_authority(request):

    if request.method == "POST":
        form = AuthorityForm(request.POST, request.FILES)

        if form.is_valid():

            # ملاحظة: هذا هو الشرط الجديد لمنع تكرار نوع الهيئة فقط
            selected_type = form.cleaned_data["type"]
            if Authority.objects.filter(type=selected_type).exists():
                messages.error(request, "هذا النوع من الهيئات مستخدم مسبقًا ولا يمكن إضافته مرة أخرى.")
                return redirect("add_authority")

            authority = form.save(commit=False)
            authority.owner = request.user
            authority.save()

            messages.success(request, "تم إضافة الهيئة بنجاح")
            return redirect('add_museum', authority_id=authority.id)

    else:
        form = AuthorityForm()

    return render(request, 'museum/add_authority.html', {"form": form})


# عرض جميع الهيئات
def all_authority(request):
    authority_type = request.GET.get("type")

    if authority_type:
        authorities = Authority.objects.filter(type_id=authority_type)
    else:
        authorities = Authority.objects.all().order_by("-id")

    types = AuthorityType.objects.all()

    return render(request, 'museum/all_authority.html', {
        "authorities": authorities,
        "types": types,
        "selected": authority_type,
    })


# تحديث الهيئة
def update_authority(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)

    if request.method == "POST":
        form = AuthorityForm(request.POST, request.FILES, instance=authority)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الهيئة بنجاح")
            return redirect('all_authority')

    else:
        form = AuthorityForm(instance=authority)

    return render(request, 'museum/add_authority.html', {
        "form": form,
        "update_mode": True,
    })


# حذف هيئة
def delete_authority(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)
    authority.delete()
    messages.success(request, "تم حذف الهيئة بنجاح")
    return redirect('all_authority')


# إضافة متحف للهيئة
def add_museum(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)

    if request.method == "POST":
        form = MuseumForm(request.POST, request.FILES)

        if form.is_valid():
            museum = form.save(commit=False)
            museum.authority = authority
            museum.save()

            messages.success(request, "تمت إضافة المتحف للهيئة بنجاح")
            return redirect('add_museum', authority_id=authority_id)

    else:
        form = MuseumForm()

    return render(request, 'museum/add_museum.html', {
        "form": form,
        "authority": authority
    })


# تفاصيل الهيئة
def details(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)
    museums = Museum.objects.filter(authority=authority)

    return render(request, 'museum/details.html', {
        "authority": authority,
        "museums": museums
    })


def all_del_museum(request):
    return render(request, 'museum/all_del_museum.html')


# الحجز
def booking(request):
    authorities = Authority.objects.all()
    museums = Museum.objects.all()

    context = {
        'authorities': authorities,
        'museums': museums,
    }
    return render(request, 'museum/booking.html', context)


def search(request):
    return render(request, 'museum/search.html')


# API
def museums_by_authority(request, authority_id):
    museums = Museum.objects.filter(authority_id=authority_id)
    data = [{"id": m.id, "name": m.name} for m in museums]
    return JsonResponse(data, safe=False)


# حذف متحف
def delete_museum(request, museum_id):
    museum = get_object_or_404(Museum, id=museum_id)
    authority_id = museum.authority.id
    museum.delete()
    messages.success(request, "تم حذف المتحف بنجاح")
    return redirect('details', authority_id=authority_id)


# تعديل متحف
def update_museum(request, museum_id):
    museum = get_object_or_404(Museum, id=museum_id)
    authority_id = museum.authority.id

    if request.method == "POST":
        form = MuseumForm(request.POST, request.FILES, instance=museum)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل المتحف بنجاح")
            return redirect('details', authority_id=authority_id)

    else:
        form = MuseumForm(instance=museum)

    return render(request, 'museum/add_museum.html', {
        "form": form,
        "authority": museum.authority,
        "update_mode": True,
    })
