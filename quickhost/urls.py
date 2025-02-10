from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from quickhost.api.viewsets import (
    AccommodationViewSet,
    UserViewSet,
    CustomTokenObtainPairView,
    GetByUuidView,
    ReviewViewSet,
    BookingViewSet,
    FavoritePropertyViewSet,
)

router = routers.DefaultRouter()
router.register(r"accommodations", AccommodationViewSet, basename="accommodations")
router.register(r"users", UserViewSet, basename="users")
router.register(r"reviews", ReviewViewSet, basename="reviews")
router.register(r"bookings", BookingViewSet, basename="booking")
router.register(r"favorites", FavoritePropertyViewSet, basename="favorites")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
    path(
        "users/",
        UserViewSet.as_view({"get": "list", "post": "create"}),
        name="user_list",
    ),
    path(
        "users/<uuid:id_user>/",
        UserViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="user_detail",
    ),
    path(
        "accommodations/<uuid:id_accommodation>/",
        AccommodationViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="accommodation_detail",
    ),
    path(
        "users/<uuid:id_user>/accommodations/",
        AccommodationViewSet.as_view({"post": "create"}),
        name="create_accommodation",
    ),
    path("details/", GetByUuidView.as_view(), name="details"),
    path(
        "reviews/",
        ReviewViewSet.as_view({"get": "list", "post": "create"}),
        name="review-list-create",
    ),
    path(
        "reviews/<uuid:id_review>/",
        ReviewViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="review-detail",
    ),
    path(
        "bookings/",
        BookingViewSet.as_view({"get": "list", "post": "create"}),
        name="booking-list-create",
    ),
    path(
        "bookings/<uuid:id_booking>/",
        BookingViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="booking-detail",
    ),
    path(
        "favorites/",
        FavoritePropertyViewSet.as_view({"get": "retrieve", "post": "create"}),
        name="favorites",
    ),
    path(
        "favorites/<uuid:id_favorite_property>/",
        FavoritePropertyViewSet.as_view(
            {"get": "retrieve", "post": "create", "delete": "destroy"}
        ),
        name="favorite-detail",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
