from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import Contact
import os


def contact_us(request):

    #  منع غير المسجلين دخول من الإرسال
    if request.method == "POST" and not request.user.is_authenticated:
        messages.error(request, "يجب تسجيل الدخول قبل إرسال الرسالة.")
        return redirect("account:sign_in")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            message=message
        )

        send_mail(
            subject="New Contact Form Message",
            message=f"From: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\n\n{message}",
            from_email=os.getenv("EMAIL_HOST_USER"),
            recipient_list=[os.getenv("EMAIL_HOST_USER")],
        )

        messages.success(request, "تم إرسال رسالتك بنجاح!")
        return redirect("contact_us")

    return render(request, "contact/contact_us.html")