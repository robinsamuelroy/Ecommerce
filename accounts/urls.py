from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
  path('sign-up/', views.register_view, name='signup'),
  path('login/', views.login_view, name='login'),
  path('logout/', views.logoutUser, name='logout'),
  path('sign-up/otp_verification',views.otp_verification,name="otp_verification"),


  path('reset-password/', views.forgot_password, name='reset_password'),
  path('reset-password/verify-otp/', views.verify_otp, name='verify_otp'),
  path('reset-password/confirm/', views.reset_password_confirm, name='reset_password_confirm'),
]

