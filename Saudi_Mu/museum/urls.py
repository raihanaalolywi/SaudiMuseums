from django.urls import path
from . import views

urlpatterns = [
    # مسار إضافة متحف لهيئة معينة
    path('museum/add/<int:authority_id>/', views.add_museum, name='add_museum'),
    
    path('authority/add/', views.add_authority, name='add_authority'),
    path('authority/all/', views.all_authority, name='all_authority'),

    path('booking/', views.booking, name='booking'),

    # مسار تفاصيل الهيئة
    path('details/<int:authority_id>/', views.details, name='details'),

    path('search/', views.search, name='search'),

    # مسار جلب المتاحف التابعة لهيئة API
    path('api/museums/<int:authority_id>/', views.museums_by_authority, name='museums_by_authority'),

    # مسار تحديث الهيئة
    path('authority/update/<int:authority_id>/', views.update_authority, name='update_authority'),

    # مسار حذف الهيئة
    path('authority/delete/<int:authority_id>/', views.delete_authority, name='delete_authority'),

    # مسار حذف المتحف
    path('museum/delete/<int:museum_id>/', views.delete_museum, name='delete_museum'),

    # هنا الإضافة الجديدة: تحديث المتحف
    path('museum/update/<int:museum_id>/', views.update_museum, name='update_museum'),
]
