from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction, IntegrityError
from .models import Profile
from museum.models import Authority, Museum
from museum.models import Bookmark
from museum.models import Booking, Bookmark

# -----------------------------
# Sign Up
# -----------------------------
def sign_up(request):
    if request.method == "POST":
        try:
            account_type = request.POST.get("account_type")

            with transaction.atomic():
                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password"],
                    email=request.POST["email"],
                    first_name=request.POST["first_name"],
                    last_name=request.POST["last_name"]
                )

                if account_type == "user":
                    Profile.objects.create(
                        user=new_user, 
                        avatar=request.FILES.get("avatar")
                    )
                    redirect_url = "account:user_profile_view"
                    redirect_args = {"user_name": new_user.username}
                    success_msg = f"Welcome {new_user.first_name}! Your account has been created successfully."

                elif account_type == "authority":
                    authority = Authority.objects.create(
                        owner=new_user,
                        name=f"New Authority ({new_user.username})",
                        image=request.FILES.get("avatar")
                    )
                    redirect_url = "account:authority_profile"
                    redirect_args = {"authority_id": authority.id}
                    success_msg = f"Authority account created successfully! Welcome aboard."

                else:
                    messages.error(request, "Please select a valid account type.")
                    return redirect("account:sign_up")

            login(request, new_user)
            messages.success(request, success_msg)
            return redirect(redirect_url, **redirect_args)

        except IntegrityError:
            messages.error(request, "Username already exists. Please choose another username.")
            return redirect("account:sign_up")
        except Exception as e:
            messages.error(request, "Couldn't create account. Please try again.")
            print(f"Sign up error: {e}")
            return redirect("account:sign_up")

    return render(request, "account/signup.html")


# -----------------------------
# Sign In
# -----------------------------
def sign_in(request: HttpRequest):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            
            if user.authority_set.exists():
                authority = user.authority_set.first()
                messages.success(request, f"Welcome back, {authority.name}!", extra_tags="success")
                return redirect('account:authority_profile', authority_id=authority.id)
            else:
                profile, _ = Profile.objects.get_or_create(user=user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!", extra_tags="success")
                return redirect('account:user_profile_view', user_name=user.username)
        else:
            # هنا بدل extra_tags="error" استعمل Bootstrap class "danger"
            messages.error(request, "Invalid username or password. Please try again.", extra_tags="danger")
    
    return render(request, "account/signin.html")


# -----------------------------
# Log Out
# -----------------------------
def log_out(request: HttpRequest):
    user_name = request.user.first_name or request.user.username
    logout(request)
    messages.success(request, f"Goodbye {user_name}! You've been logged out successfully.")
    return redirect("home")


# -----------------------------
# User Profile View
# -----------------------------
def user_profile_view(request: HttpRequest, user_name):
    try:
        user = User.objects.get(username=user_name)
        profile, _ = Profile.objects.get_or_create(user=user)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("home")
    
    bookmarks = Bookmark.objects.filter(user=user).select_related('museum')

    # كل الـ bookings (زيارات المتاحف)
    bookings = Booking.objects.filter(user=user).select_related('museum', 'museum__authority').order_by('-booked_at')


    context = {
        "user": user,
        "profile": profile,
        "bookmarks": bookmarks,
        "bookmarks_count": bookmarks.count(),
        "visited_museums": bookings,
        "visited_museums_count": bookings.count(),
    }
    return render(request, 'account/profile.html', context)


# -----------------------------
# Authority Profile View
# -----------------------------
def authority_profile(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)
    museums_list = Museum.objects.filter(authority=authority)
    museums_count = museums_list.count()

    context = {
        "authority": authority,
        "museums_list": museums_list,
        "museums_count": museums_count,
    }
    return render(request, 'account/authority_profile.html', context)


# -----------------------------
# Update Authority Profile
# -----------------------------
def update_authority_profile(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)

    if request.user != authority.owner:
        messages.warning(request, "You don't have permission to edit this profile.")
        return redirect('home')

    if request.method == "POST":
        try:
            authority.name = request.POST.get("name")
            authority.description = request.POST.get("description")
            authority.website_link = request.POST.get("website_link")
            authority.location = request.POST.get("location")

            if "image" in request.FILES:
                authority.image = request.FILES["image"]

            authority.save()
            messages.success(request, "Authority profile updated successfully!")
            return redirect('account:authority_profile', authority_id=authority.id)
        except Exception as e:
            messages.error(request, "Couldn't update profile. Please try again.")
            print(f"Update authority error: {e}")

    return render(request, "account/update_authority_profile.html", {"authority": authority})


# -----------------------------
# Update User Profile
# -----------------------------
def update_user_profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to update your profile.")
        return redirect("account:sign_in")

    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        try:
            with transaction.atomic():
                user.first_name = request.POST.get("first_name", user.first_name)
                user.last_name = request.POST.get("last_name", user.last_name)
                user.email = request.POST.get("email", user.email)
                user.save()

                profile.about = request.POST.get("about", profile.about)
                if request.FILES.get("avatar"):
                    profile.avatar = request.FILES["avatar"]
                profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("account:user_profile_view", user_name=user.username)
        except Exception as e:
            messages.error(request, "Couldn't update profile. Please try again.")
            print(f"Update profile error: {e}")

    context = {"user": user, "profile": profile}
    return render(request, "account/update_profile.html", context)




