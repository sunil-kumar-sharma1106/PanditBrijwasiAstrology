from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="astrology/login.html"
        ),
        name="login"
    ),
    path(
    "register/",
    views.register,
    name="register"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
    "logout/",
    auth_views.LogoutView.as_view(),
    name="logout"
    ),

    path(
        "rashifal/<str:zodiac>/",
        views.rashifal_detail,
        name="rashifal_detail"
    ),
    path(
    "janam-kundli/",
    views.janam_kundli,
    name="janam_kundli"
    ),

    path(
    "kundli-milan/",
    views.kundli_milan,
    name="kundli_milan"
    ),

    path(
    "career-astrology/",
    views.career_astrology,
    name="career_astrology"
    ),

    path(
    "finance-business/",
    views.finance_business,
    name="finance_business"
    ),

    path(
    "numerology/",
    views.numerology,
    name="numerology"
    ),

    path(
    "gemstone-guidance/",
    views.gemstone_guidance,
    name="gemstone_guidance"
    ),


    path(
        "premium/",
        views.premium_plans,
        name="premium_plans"
    ),
    path(
        "premium/checkout/<str:plan>/",
        views.premium_checkout,
        name="premium_checkout"
    ),
    path(
        "premium/payment/<int:subscription_id>/",
        views.premium_payment,
        name="premium_payment",
    ),
    path(
        "premium/verify/<int:subscription_id>/",
        views.premium_verify_payment,
        name="premium_verify_payment",
    ),
    path(
        "premium/success/<int:subscription_id>/",
        views.premium_success,
        name="premium_success",
    ),
    
]