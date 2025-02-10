from django.db.models import UniqueConstraint, Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from .validators import (
    validate_room_count,
    validate_bed_count,
    validate_bathroom_count,
    validate_guest_capacity,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Defina o email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class UserAccount(AbstractUser):
    id_user = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    social_name = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    cpf = models.CharField(max_length=11, blank=True, null=True)
    registered_accommodations = models.ManyToManyField(
        "PropertyListing", blank=True, related_name="users_registered"
    )
    registered_accommodation_bookings = models.ManyToManyField("Booking", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.id_user}"


class PropertyListing(models.Model):
    id_accommodation = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    creator = models.ForeignKey(
        "UserAccount", on_delete=models.CASCADE, related_name="accommodations"
    )
    consecutive_days_limit = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "Número de dias consecutivos permitido. Deixe em branco para ilimitado."
        ),
    )
    main_cover_image = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    internal_images = models.JSONField(blank=True, null=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00, blank=True
    )
    registered_user_bookings = models.ManyToManyField(
        "Booking", related_name="registered_accommodations", blank=True
    )
    registered_accommodation_bookings = models.ManyToManyField(
        "PropertyListing", blank=True
    )
    discount = models.BooleanField(default=False)
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, blank=True, null=True
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, blank=True, null=True
    )
    CATEGORY_CHOICES = [
        ("inn", _("Inn")),
        ("chalet", _("Chalet")),
        ("apartment", _("Apartment")),
        ("home", _("Home")),
        ("room", _("Room")),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="inn")
    room_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)], default=1
    )
    bed_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)], default=1
    )
    bathroom_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)], default=1
    )
    guest_capacity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)], default=1
    )
    SPACE_TYPE_CHOICES = [
        ("full_space", _("Full Space")),
        ("limited_space", _("Limited Space")),
    ]
    space_type = models.CharField(
        max_length=50, choices=SPACE_TYPE_CHOICES, default="full_space"
    )
    address = models.CharField(max_length=255, default=_("Not informed"))
    city = models.CharField(max_length=100, default=_("Not informed"))
    neighborhood = models.CharField(max_length=100, default=_("Not informed"))
    postal_code = models.CharField(max_length=10, default=_("Not informed"))
    uf = models.CharField(max_length=10, default=_("Not informed"), blank=True)
    wifi = models.BooleanField(default=False)
    tv = models.BooleanField(default=False)
    kitchen = models.BooleanField(default=False)
    washing_machine = models.BooleanField(default=False)
    parking_included = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    jacuzzi = models.BooleanField(default=False)
    grill = models.BooleanField(default=False)
    private_gym = models.BooleanField(default=False)
    beach_access = models.BooleanField(default=False)
    smoke_detector = models.BooleanField(default=False)
    fire_extinguisher = models.BooleanField(default=False)
    first_aid_kit = models.BooleanField(default=False)
    outdoor_camera = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title or _("Accommodation without title")

    def calculate_final_price(self):
        """Calcula o preço final da acomodação com base no preço por noite e a taxa de limpeza."""
        total_cost = self.price_per_night + self.cleaning_fee
        return total_cost

    def save(self, *args, **kwargs):
        validate_room_count(self.room_count)
        validate_bed_count(self.bed_count)
        validate_bathroom_count(self.bathroom_count)
        validate_guest_capacity(self.guest_capacity)
        self.final_price = self.calculate_final_price()

        if self.main_cover_image and self.main_cover_image not in self.internal_images:
            raise ValidationError(
                _("The cover image must be one of the internal images.")
            )
        super().save(*args, **kwargs)


class Booking(models.Model):
    id_booking = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_booking = models.ForeignKey(
        "UserAccount",
        on_delete=models.CASCADE,
        related_name="user_bookings",
    )
    accommodation = models.ForeignKey(
        "PropertyListing",
        on_delete=models.CASCADE,
        related_name="accommodation_bookings",
    )
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Reserva de {self.user_booking.username} para {self.accommodation.title}"
        )


class FavoriteProperty(models.Model):
    id_favorite_property = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
    )
    user_favorite_property = models.ForeignKey("UserAccount", on_delete=models.CASCADE)
    accommodation = models.ForeignKey("PropertyListing", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_favorite_property", "accommodation"],
                name="unique_user_accommodation_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user_favorite_property.username} - {self.accommodation.title}"


class Review(models.Model):
    id_review = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    accommodation = models.ForeignKey(
        "PropertyListing", on_delete=models.CASCADE, related_name="reviews"
    )
    user_comment = models.ForeignKey(
        "UserAccount", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(null=False)
    comment = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id_review} for accommodation {self.accommodation.id_accommodation}"
