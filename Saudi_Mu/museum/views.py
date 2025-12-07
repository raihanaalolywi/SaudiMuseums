from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Authority, AuthorityType, Museum
from .forms import AuthorityForm, MuseumForm
from .models import Authority, Museum, MuseumComment  # اضفت تعديل هنا 
from django.core.paginator import Paginator # اضفت برضو هنا سطر اضافي  لعملية  pagination
from museum.models import Bookmark
from .models import Museum, Booking

@login_required(login_url='account:sign_in')
def add_authority(request):
    # فقط المستخدمين الذين سجلوا كهيئة يمكنهم إضافة الهيئة
    profile = getattr(request.user, 'profile', None)
    if not profile:
        messages.error(request, "يرجى إنشاء حساب أولاً.")
        return redirect('account:sign_up')

    if request.method == "POST":
        form = AuthorityForm(request.POST, request.FILES)
        if form.is_valid():
            selected_type = form.cleaned_data["type"]
            if Authority.objects.filter(type=selected_type).exists():
                messages.error(request, "هذا النوع من الهيئات مستخدم مسبقًا ولا يمكن إضافته مرة أخرى.")
                return redirect("add_authority")

            authority = form.save(commit=False)
            authority.owner = request.user
            authority.save()

            messages.success(request, "تم إضافة الهيئة بنجاح")
            # بعد إضافة الهيئة، إعادة التوجيه مباشرة لبروفايل الهيئة
            return redirect('account:authority_profile', authority_id=authority.id)

    else:
        form = AuthorityForm()

    return render(request, 'museum/add_authority.html', {"form": form})


# عرض جميع الهيئات

def all_authority(request):
    authority_type = request.GET.get("type")

    if authority_type:
          authorities_list = Authority.objects.filter(type_id=authority_type).order_by("id")
    else:
         authorities_list = Authority.objects.all().order_by("id")


    # Pagination: 3 هيئات لكل صفحة
    paginator = Paginator(authorities_list, 3)
    page_number = request.GET.get('page')
    authorities = paginator.get_page(page_number)

    types = AuthorityType.objects.all()

    return render(request, 'museum/all_authority.html', {
        "authorities": authorities,
        "types": types,
        "selected": authority_type,
        "paginator": paginator,  # لإظهار أزرار الصفحات
    })



# تحديث الهيئة
@login_required(login_url='account:sign_in')
def update_authority(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)

    # تحقق إذا المستخدم هو المالك أو أدمن
    if request.user != authority.owner and not request.user.is_staff:
        messages.error(request, "ليس لديك صلاحية تعديل هذه الهيئة")
        return redirect('home')  # ارجاع للصفحة الرئيسية

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


@login_required(login_url='account:sign_in')
def delete_authority(request, authority_id):

    # أول شيء نجيب الهيئة
    authority = get_object_or_404(Authority, id=authority_id)

    # بعدها نسوي التحقق
    if request.user != authority.owner and not request.user.is_staff:
        messages.error(request, "ليس لديك صلاحية حذف هذه الهيئة")
        return redirect('home')

    # بعدها نحذف
    authority.delete()
    messages.success(request, "تم حذف الهيئة بنجاح")
    return redirect('all_authority')


# إضافة متحف للهيئة
def add_museum(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)
    
     # تحقق من أن المستخدم هو صاحب الهيئة
    # تحقق أن صاحب الهيئة هو المستخدم
    if request.user != authority.owner:
        return redirect('home')
    
    if request.method == "POST":
        form = MuseumForm(request.POST, request.FILES)

        if form.is_valid():
            museum = form.save(commit=False)
            museum.authority = authority
            museum.save()
            messages.success(request, "The museum has been successfully added to the authority")
            return redirect('add_museum', authority_id=authority_id)

    else:
        form = MuseumForm()

    return render(request, 'museum/add_museum.html', {
        "form": form,
        "authority": authority
    })

# هنا عدلت عليه لاجل اضافة تعليق 
def details(request, authority_id):
    is_authority = Authority.objects.filter(owner=request.user).exists()

    authority = get_object_or_404(Authority, id=authority_id)
    museums = Museum.objects.filter(authority=authority)

  
    

    # استقبال تعليق جديد
    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")  # يمنع مستخدم غير مسجل دخول

        comment_text = request.POST.get("comment")
        rating = request.POST.get("rating")
        museum_id = request.POST.get("museum_id")

        # جلب المتحف المُختار من القائمة
        museum = get_object_or_404(Museum, id=museum_id)

        # إنشاء التعليق
        MuseumComment.objects.create(
            museum=museum,
            user=request.user,
            comment=comment_text,
            rating=rating
        )

        return redirect("details", authority_id=authority.id)
    
 
    #  هنا نضيف ال Pagination لعرض التعليقات 
  
    all_comments = MuseumComment.objects.filter(
        museum__authority=authority
    ).order_by("-created_at")

    from django.core.paginator import Paginator
    paginator = Paginator(all_comments, 3)  # 3 تعليقات لكل صفحة
    page_number = request.GET.get("page")
    comments_page = paginator.get_page(page_number)

    # تجهيز التعليقات لكل متحف (كودك القديم ما نلمسه)
    museums_with_comments = []
    for museum in museums:
        comments = museum.comments.all().order_by("-created_at")
        museums_with_comments.append((museum, comments))

    return render(request, "museum/details.html", {
        "authority": authority,
        "museums_with_comments": museums_with_comments,
        "museums": museums,
        
        #  نرسل صفحة التعليقات للـ HTML
        "comments_page": comments_page,

    })




def all_del_museum(request):
    return render(request, 'museum/all_del_museum.html')


# الحجز

@login_required
def add_booking(request, museum_id):
    museum = get_object_or_404(Museum, id=museum_id)
    booking, created = Booking.objects.get_or_create(user=request.user, museum=museum)
    
    if created:
        messages.success(request, "تم حجز المتحف بنجاح!")
    else:
        messages.info(request, "لقد قمت بحجز هذا المتحف مسبقًا.")
    
    return redirect('account:user_profile', user_name=request.user.username)


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




def search(request):
    query = request.GET.get('q', '').strip()

    authorities = Authority.objects.filter(name__icontains=query) if query else Authority.objects.none()
    museums = Museum.objects.filter(name__icontains=query) if query else Museum.objects.none()

    context = {
        'authorities': authorities,
        'museums': museums,
    }
    return render(request, 'museum/search_results.html', context)








def add_museum_bookmark(request, museum_id):
    if not request.user.is_authenticated:
        messages.error(request, "يجب تسجيل الدخول أولاً لإضافة المتحف للمفضلة")
        return redirect('account:sign_in')

    museum = get_object_or_404(Museum, id=museum_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, museum=museum)

    if created:
        messages.success(request, "تمت إضافة المتحف للمفضلة!")
    else:
        messages.info(request, "هذا المتحف موجود بالفعل في المفضلة")

    return redirect(request.META.get('HTTP_REFERER', '/'))




def booking(request):
    authorities = Authority.objects.all()
    museums = Museum.objects.all()

    if request.method == "POST":
        museum_id = request.POST.get("museum")
        if museum_id:
            museum = get_object_or_404(Museum, id=museum_id)
            booking, created = Booking.objects.get_or_create(user=request.user, museum=museum)
            if created:
                messages.success(request, "تم حجز المتحف بنجاح!")
            else:
                messages.info(request, "لقد قمت بحجز هذا المتحف مسبقًا.")
            return redirect('account:user_profile_view', user_name=request.user.username)

    context = {
        'authorities': authorities,
        'museums': museums,
    }
    return render(request, 'museum/booking.html', context)






