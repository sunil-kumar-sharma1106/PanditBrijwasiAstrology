from django.db import models
from django.utils import timezone


# ============================================================
# HOROSCOPE MODEL
# ============================================================

class Horoscope(models.Model):

    ZODIAC_CHOICES = [
        ("aries", "Aries"),
        ("taurus", "Taurus"),
        ("gemini", "Gemini"),
        ("cancer", "Cancer"),
        ("leo", "Leo"),
        ("virgo", "Virgo"),
        ("libra", "Libra"),
        ("scorpio", "Scorpio"),
        ("sagittarius", "Sagittarius"),
        ("capricorn", "Capricorn"),
        ("aquarius", "Aquarius"),
        ("pisces", "Pisces"),
    ]

    zodiac = models.CharField(
        max_length=20,
        choices=ZODIAC_CHOICES
    )

    date = models.DateField()

    # Normal daily horoscope prediction
    prediction = models.TextField()

    # Premium horoscope prediction
    premium_prediction = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["zodiac", "-date"]

        constraints = [
            models.UniqueConstraint(
                fields=["zodiac", "date"],
                name="unique_daily_horoscope"
            )
        ]

    def __str__(self):
        return f"{self.get_zodiac_display()} - {self.date}"


# ============================================================
# PREMIUM SUBSCRIPTION MODEL
# ============================================================

class PremiumSubscription(models.Model):

    PLAN_CHOICES = [
        ("7_days", "7 Days"),
        ("1_month", "1 Month"),
        ("3_months", "3 Months"),
        ("1_year", "1 Year"),
    ]

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="premium_subscriptions"
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    start_date = models.DateTimeField(
        null=True,
        blank=True
    )

    expiry_date = models.DateTimeField(
        null=True,
        blank=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        default="pending"
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"

    # Check whether premium subscription is currently active
    @property
    def is_active(self):
        return (
            self.payment_status == "success"
            and self.expiry_date is not None
            and self.expiry_date > timezone.now()
        )


# ============================================================
# DAILY DARSHAN MODEL
# ============================================================

class DailyDarshan(models.Model):

    CATEGORY_CHOICES = [
        ("mahakaleshwar", "Mahakaleshwar"),
        ("balaji", "Balaji"),
        ("khatu_shyam", "Khatu Shyam Ji"),
        ("vaishno_devi", "Vaishno Devi"),
    ]

    title = models.CharField(
        max_length=200
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    date = models.DateField()

    # Darshan image
    image = models.ImageField(
        upload_to="darshan/"
    )

    # YouTube video URL
    youtube_url = models.URLField()

    # Optional local video file
    video = models.FileField(
        upload_to="darshan/videos/",
        blank=True,
        null=True
    )

    # ========================================================
    # YOUTUBE EMBED URL
    # Converts normal YouTube links into embed links
    # ========================================================

    @property
    def youtube_embed_url(self):

        if not self.youtube_url:
            return ""

        url = self.youtube_url

        # Example:
        # https://youtu.be/VIDEO_ID
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        # Example:
        # https://www.youtube.com/watch?v=VIDEO_ID
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        # Example:
        # https://www.youtube.com/shorts/VIDEO_ID
        if "/shorts/" in url:
            video_id = url.split("/shorts/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        return url

    # Darshan description
    description = models.TextField(
        blank=True
    )

    # Whether this Darshan should be visible on website
    is_published = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.date}"


# ============================================================
# JANAM KUNDLI MODEL
# ============================================================

class JanamKundli(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="janam_kundlis"
    )

    birth_date = models.DateField()

    birth_time = models.TimeField()

    birth_place = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.birth_date} - "
            f"{self.birth_place}"
        )