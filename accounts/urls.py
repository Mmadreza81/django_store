from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('verify/', views.UserRegisterVerifyCodeView.as_view(), name='verify_code'),
    path('resend/', views.ResendOtpCodeView.as_view(), name='resend_code'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('user_profile/<int:user_id>/', views.UserProfileView.as_view(), name='user_profile'),
    path('reset/', views.UserPasswordResetView.as_view(), name='reset_password'),
    path('reset/done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('confirm/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('edit_user/', views.EditUserView.as_view(), name='edit_user'),
    path('addresses/', views.ManageAddressView.as_view(), name='manage_addresses'),
]
