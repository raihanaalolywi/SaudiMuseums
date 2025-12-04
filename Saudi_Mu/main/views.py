from django.shortcuts import render
from museum.models import Authority
from museum.models import Museum



def home_view(request):
    # آخر هيئتين
    authorities = Authority.objects.all().order_by('-id')[:3]

    # آخر 6 متاحف
    museums = Museum.objects.all().order_by('-id')[:3]

    return render(request, 'main/home.html', {
        'authorities': authorities,
        'museums': museums,
    })




