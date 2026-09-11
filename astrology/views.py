from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from datetime import timedelta


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Horoscope, PremiumSubscription, DailyDarshan
import razorpay

# =========================================================
# RAZORPAY CLIENT
# =========================================================

razorpay_client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET,
    )
)


# =========================================================
# PLAN CONFIGURATION
# =========================================================

PREMIUM_PLANS = {
    "7_days": {
        "name": "7 Days",
        "price": 99,
        "duration": timedelta(days=7),
    },
    "1_month": {
        "name": "1 Month",
        "price": 299,
        "duration": timedelta(days=30),
    },
    "3_months": {
        "name": "3 Months",
        "price": 699,
        "duration": timedelta(days=90),
    },
    "1_year": {
        "name": "1 Year",
        "price": 1999,
        "duration": timedelta(days=365),
    },
}


# =========================================================
# PREMIUM STATUS
# =========================================================

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
                "Active premium subscription required.",
            )
            return redirect("premium_plans")

        return view_func(request, *args, **kwargs)

    return wrapper


def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not password:
            messages.error(
                request,
                "Username and password are required."
            )
            return redirect("register")

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return redirect("register")

        if email and User.objects.filter(email=email).exists():
            messages.error(
                request,
                "Email already registered."
            )
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("dashboard")

    return render(
        request,
        "astrology/register.html"
    )

# =========================================================
# HOME
# =========================================================

def home(request):

    today = timezone.localdate()

    horoscopes = Horoscope.objects.filter(
        date=today
    )

    daily_darshans = DailyDarshan.objects.filter(
        is_published=True
    ).order_by(
        "-date",
        "-created_at"
    )[:4]

    return render(
        request,
        "astrology/home.html",
        {
            "horoscopes": horoscopes,
            "daily_darshans": daily_darshans,
        },
    )

# =========================================================
# RASHIFAL DETAIL
# =========================================================

def rashifal_detail(request, zodiac):

    today = timezone.localdate()

    horoscope = get_object_or_404(
        Horoscope,
        zodiac=zodiac,
        date=today,
    )

    premium_active = False

    if request.user.is_authenticated:
        premium_active = has_active_premium(request.user)

    return render(
        request,
        "astrology/rashifal_detail.html",
        {
            "horoscope": horoscope,
            "premium_active": premium_active,
        },
    )


# =========================================================
# ASTROLOGY SERVICES
# =========================================================

def janam_kundli(request):

    if request.method == "POST":

        birth_date = request.POST.get("birth_date")
        birth_time = request.POST.get("birth_time")
        birth_place = request.POST.get("birth_place", "").strip()

        if not birth_date or not birth_time or not birth_place:
            messages.error(
                request,
                "Please enter your birth date, birth time and birth place."
            )

            return render(
                request,
                "astrology/janam_kundli.html"
            )

        return render(
            request,
            "astrology/janam_kundli_result.html",
            {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "birth_place": birth_place,
            },
        )

    return render(
        request,
        "astrology/janam_kundli.html"
    )


def kundli_milan(request):
    return render(
        request,
        "astrology/kundli_milan.html"
    )


def career_astrology(request):
    return render(
        request,
        "astrology/career_astrology.html"
    )


def finance_business(request):
    return render(
        request,
        "astrology/finance_business.html"
    )


def numerology(request):
    return render(
        request,
        "astrology/numerology.html"
    )


def gemstone_guidance(request):
    return render(
        request,
        "astrology/gemstone_guidance.html"
    )

# =========================================================
# PREMIUM PLANS
# =========================================================

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
        },
    )


# =========================================================
# PREMIUM CHECKOUT
# =========================================================

@login_required
def premium_checkout(request, plan):

    selected_plan = PREMIUM_PLANS.get(plan)

    if not selected_plan:
        from django.http import Http404
        raise Http404("Invalid subscription plan")

    # -----------------------------------------------------
    # Reuse an existing pending subscription
    # -----------------------------------------------------

    pending_subscription = PremiumSubscription.objects.filter(
        user=request.user,
        plan=plan,
        payment_status="pending",
    ).order_by("-created_at").first()

    if pending_subscription:

        return render(
            request,
            "astrology/premium_checkout.html",
            {
                "selected_plan": selected_plan,
                "subscription": pending_subscription,
            },
        )

    # -----------------------------------------------------
    # Create new subscription
    # -----------------------------------------------------

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
        },
    )


# =========================================================
# PREMIUM PAYMENT
# =========================================================

@login_required
def premium_payment(request, subscription_id):

    subscription = get_object_or_404(
        PremiumSubscription,
        id=subscription_id,
        user=request.user,
    )

    # Don't allow payment for an already successful subscription
    if subscription.payment_status == "success":

        return redirect(
            "premium_success",
            subscription_id=subscription.id,
        )

    # -----------------------------------------------------
    # Create Razorpay order
    # -----------------------------------------------------

    if not subscription.razorpay_order_id:

        amount_paise = int(
            subscription.amount * 100
        )

        razorpay_order = razorpay_client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"premium_{subscription.id}",
            }
        )

        subscription.razorpay_order_id = razorpay_order["id"]

        subscription.save(
            update_fields=[
                "razorpay_order_id",
                "updated_at",
            ]
        )

    return render(
        request,
        "astrology/premium_payment.html",
        {
            "subscription": subscription,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": subscription.razorpay_order_id,
        },
    )


# =========================================================
# VERIFY RAZORPAY PAYMENT
# =========================================================

@login_required
def premium_verify_payment(request, subscription_id):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method.",
            },
            status=405,
        )

    subscription = get_object_or_404(
        PremiumSubscription,
        id=subscription_id,
        user=request.user,
    )

    # -----------------------------------------------------
    # Prevent duplicate activation
    # -----------------------------------------------------

    if subscription.payment_status == "success":

        return JsonResponse(
            {
                "success": True,
                "redirect_url": (
                    f"/premium/success/"
                    f"{subscription.id}/"
                ),
            }
        )

    payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    order_id = request.POST.get(
        "razorpay_order_id"
    )

    signature = request.POST.get(
        "razorpay_signature"
    )

    if not payment_id or not order_id or not signature:

        return JsonResponse(
            {
                "success": False,
                "message": "Payment verification data is missing.",
            },
            status=400,
        )

    # -----------------------------------------------------
    # Verify correct order
    # -----------------------------------------------------

    if order_id != subscription.razorpay_order_id:

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid Razorpay order.",
            },
            status=400,
        )

    # -----------------------------------------------------
    # Verify Razorpay signature
    # -----------------------------------------------------

    try:

        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )

    except razorpay.errors.SignatureVerificationError:

        subscription.payment_status = "failed"

        subscription.save(
            update_fields=[
                "payment_status",
                "updated_at",
            ]
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Payment verification failed.",
            },
            status=400,
        )

    # -----------------------------------------------------
    # Activate subscription
    # -----------------------------------------------------

    now = timezone.now()

    duration = PREMIUM_PLANS[
        subscription.plan
    ]["duration"]

    subscription.payment_status = "success"
    subscription.transaction_id = payment_id
    subscription.start_date = now
    subscription.expiry_date = now + duration

    subscription.save()

    return JsonResponse(
        {
            "success": True,
            "redirect_url": (
                f"/premium/success/"
                f"{subscription.id}/"
            ),
        }
    )


# =========================================================
# PREMIUM SUCCESS
# =========================================================

@login_required
def premium_success(request, subscription_id):

    subscription = get_object_or_404(
        PremiumSubscription,
        id=subscription_id,
        user=request.user,
    )

    return render(
        request,
        "astrology/premium_success.html",
        {
            "subscription": subscription,
        },
    )


# =========================================================
# USER DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    subscriptions = PremiumSubscription.objects.filter(
        user=request.user
    ).order_by("-created_at")

    active_subscription = subscriptions.filter(
        payment_status="success",
        expiry_date__gt=timezone.now(),
    ).first()

    return render(
        request,
        "astrology/dashboard.html",
        {
            "subscriptions": subscriptions,
            "active_subscription": active_subscription,
        },
    )