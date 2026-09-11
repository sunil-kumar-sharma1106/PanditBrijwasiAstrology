from django.contrib import admin
from .models import Horoscope, PremiumSubscription, DailyDarshan, JanamKundli


@admin.register(Horoscope)
class HoroscopeAdmin(admin.ModelAdmin):
    list_display = (
        "zodiac",
        "date",
    )

    search_fields = (
        "prediction",
        "premium_prediction",
    )

    list_filter = (
        "zodiac",
        "date",
    )


@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "amount",
        "payment_status",
        "start_date",
        "expiry_date",
    )

    list_filter = (
        "plan",
        "payment_status",
    )

    search_fields = (
        "user__username",
        "transaction_id",
        "razorpay_order_id",
    )


@admin.register(DailyDarshan)
class DailyDarshanAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "date",
        "is_published",
    )

    list_filter = (
        "category",
        "date",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
    )

    ordering = ("-date",)


@admin.register(JanamKundli)
class JanamKundliAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "birth_date",
        "birth_time",
        "birth_place",
        "created_at",
    )

    search_fields = (
        "user__username",
        "birth_place",
    )

    list_filter = (
        "birth_date",
        "created_at",
    )