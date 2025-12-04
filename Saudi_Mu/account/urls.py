from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('signup/', views.sign_up, name="sign_up"),
    path('signin/', views.sign_in, name="sign_in"),
    path('logout/', views.log_out, name="log_out"),
    path('profile/update/', views.update_user_profile, name="update_user_profile"),
    path('profile/<str:user_name>/', views.user_profile_view, name="user_profile_view"),



path('authority-profile/<int:authority_id>/', views.authority_profile, name='authority_profile'),

path('authority/update/<int:authority_id>/', views.update_authority_profile, name="update_authority_profile"),









  # غيرنا الاسم للسهولة
]
