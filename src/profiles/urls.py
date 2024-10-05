from django.urls import path, include
from . import views



urlpatterns = [
    path("profile/", views.profileIndex, name="profile_index"),
    path("profile/email_change/", views.emailChange, name="email_change"),
    path("profile/email_verify/", views.emailVerify, name="email_verify"),
    path("", include("django.contrib.auth.urls")),
]
