from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from .models import Horoscope, PremiumSubscription
from datetime import timedelta
from django.http import JsonResponse
import razorpay


razorpay_client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)


# =========================
# HOME
# =========================

def home(request):

    today = timezone.localdate()

    horoscopes = Horoscope.objects.filter(
        date=today
    )

    context = {
        "horoscopes": horoscopes,
    }

    return render(
        request,
        "astrology/home.html",
        context
    )


# =========================
# RASHIFAL DETAIL
# =========================

def rashifal_detail(request, zodiac):

    today = timezone.localdate()

    horoscope = get_object_or_404(
        Horoscope,
        zodiac=zodiac,
        date=today
    )

    premium_active = False

    if request.user.is_authenticated:
        premium_active = has_active_premium(request.user)

    context = {
        "horoscope": horoscope,
        "premium_active": premium_active,
    }

    return render(
        request,
        "astrology/rashifal_detail.html",
        context
    )


# =========================
# PREMIUM PLANS
# =========================

def premium_plans(request):

    plans = [
        {
            "id": "7_days",
            "name": "7 Days",
            "price": 99,
            "description": "Try premium astrology guidance.",
            "features": [
                "Detailed Daily Rashifal",
                "Premium Astrology Insights",
                "7 Days Premium Access",
            ],
        },
        {
            "id": "1_month",
            "name": "1 Month",
            "price": 299,
            "description": "Perfect for regular guidance.",
            "features": [
                "Detailed Daily Rashifal",
                "Numerology Insights",
                "Career & Finance Insights",
                "30 Days Premium Access",
            ],
            "popular": True,
        },
        {
            "id": "3_months",
            "name": "3 Months",
            "price": 699,
            "description": "Extended astrological guidance.",
            "features": [
                "All Premium Rashifal",
                "Numerology",
                "Career Astrology",
                "Finance & Business Insights",
                "90 Days Premium Access",
            ],
        },
        {
            "id": "1_year",
            "name": "1 Year",
            "price": 1999,
            "description": "Complete yearly premium access.",
            "features": [
                "All Premium Features",
                "Detailed Astrology Guidance",
                "Numerology",
                "Career & Finance Astrology",
                "365 Days Premium Access",
            ],
        },
    ]

    return render(
        request,
        "astrology/premium_plans.html",
        {
            "plans": plans,
        }
    )


# =========================
# PREMIUM CHECKOUT
# =========================

@login_required
def premium_checkout(request, plan):

    plans = {
        "7_days": {
            "name": "7 Days",
            "price": 99,
        },
        "1_month": {
            "name": "1 Month",
            "price": 299,
        },
        "3_months": {
            "name": "3 Months",
            "price": 699,
        },
        "1_year": {
            "name": "1 Year",
            "price": 1999,
        },
    }

    selected_plan = plans.get(plan)

    if not selected_plan:
        from django.http import Http404
        raise Http404("Invalid subscription plan")

    subscription = PremiumSubscription.objects.create(
        user=request.user,
        plan=plan,
        amount=selected_plan["price"],
        payment_status="pending",
    )

    return render(
        request,
        "astrology/premium_checkout.html",
        {
            "selected_plan": selected_plan,
            "subscription": subscription,
        }
    )


# =========================
# PREMIUM PAYMENT
# =========================

@login_required
def premium_payment(request, subscription_id):

    subscription = get_object_or_404(
        PremiumSubscription,
        id=subscription_id,
        user=request.user
    )

    if not subscription.razorpay_order_id:

        amount_paise = int(subscription.amount * 100)

        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"premium_{subscription.id}",
        })

        subscription.razorpay_order_id = razorpay_order["id"]
        subscription.save()

    context = {
        "subscription": subscription,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": subscription.razorpay_order_id,
    }

    return render(
        request,
        "astrology/premium_payment.html",
        context
    )
from django.http import JsonResponse
from datetime import timedelta


@login_required
def premium_verify_payment(request, subscription_id):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method."
            },
            status=405
        )

    subscription = get_object_or_404(
        PremiumSubscription,
        id=subscription_id,
        user=request.user
    )

    payment_id = request.POST.get("razorpay_payment_id")
    order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")

    if not payment_id or not order_id or not signature:
        return JsonResponse(
            {
                "success": False,
                "message": "Payment verification data is missing."
            },
            status=400
        )

    if order_id != subscription.razorpay_order_id:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid Razorpay order."
            },
            status=400
        )

    try:

        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })

    except razorpay.errors.SignatureVerificationError:

        subscription.payment_status = "failed"
        subscription.save()

        return JsonResponse(
            {
                "success": False,
                "message": "Payment verification failed."
            },
            status=400
        )

    # Prevent duplicate activation
    if subscription.payment_status == "success":
        return JsonResponse({
            "success": True,
            "redirect_url": f"/premium/success/{subscription.id}/"
        })

    now = timezone.now()

    duration_map = {
        "7_days": timedelta(days=7),
        "1_month": timedelta(days=30),
        "3_months": timedelta(days=90),
        "1_year": timedelta(days=365),
    }

    subscription.payment_status = "success"
    subscription.transaction_id = payment_id
    subscription.start_date = now
    subscription.expiry_date = now + duration_map[subscription.plan]

    subscription.save()

    return JsonResponse({
        "success": True,
        "redirect_url": f"/premium/success/{subscription.id}/"
    })

def has_active_premium(user):
    return PremiumSubscription.objects.filter(
        user=user,
        payment_status="success",
        expiry_date__gt=timezone.now(),
    ).exists()
def premium_required(view_func):

    @login_required
    def wrapper(request, *args, **kwargs):

        if not has_active_premium(request.user):
            messages.warning(
                request,
                "Active premium subscription required."
            )
            return redirect("premium_plans")

        return view_func(request, *args, **kwargs)

    return wrapper
# =========================
# PREMIUM SUCCESS
# =========================

@login_required
def premium_success(request, subscription_id):

    subscription = get_object_or_404(
        PremiumSubscription,
        id=subscription_id,
        user=request.user
    )

    return render(
        request,
        "astrology/premium_success.html",
        {
            "subscription": subscription,
        }
    )
# =========================
# USER DASHBOARD
# =========================

@login_required
def dashboard(request):

    subscriptions = PremiumSubscription.objects.filter(
        user=request.user
    ).order_by("-created_at")

    active_subscription = subscriptions.filter(
        payment_status="success",
        expiry_date__gt=timezone.now()
    ).first()

    context = {
        "subscriptions": subscriptions,
        "active_subscription": active_subscription,
    }

    return render(
        request,
        "astrology/dashboard.html",
        context
    )