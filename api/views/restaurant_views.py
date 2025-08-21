from api.models import editLog
from django.forms.models import model_to_dict
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import transaction

from ..models import Restaurant

# Try to import a shared serializer; if not present, use a local fallback
try:
    from ..serializers import RestaurantSerializer  # type: ignore
except Exception:
    from rest_framework import serializers

    class RestaurantSerializer(serializers.ModelSerializer):
        class Meta:
            model = Restaurant
            fields = "__all__"


class IsAuthenticatedOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    pass


class RestaurantViewSet(viewsets.ModelViewSet):
    """CRUD for Restaurant with role-based access and edit logging.

    - Admin, GeneralManager, Manager: can create, update, delete, and view restaurants.
    - Employees: can only read their own restaurant.
    - Logs create/update/delete to editLog.
    """

    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Restaurant.objects.all().order_by("name")
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return qs.none()
        role = getattr(user, "role", None)
        if role == "Admin":
            return qs
        if role in ("GeneralManager", "Manager"):
            return qs.filter(id=getattr(user, "restaurant_id", None))
        # Employees: read only their own restaurant
        return qs.filter(id=getattr(user, "restaurant_id", None))

    def perform_create(self, serializer):
        role = getattr(self.request.user, "role", None)
        if role not in ("Admin", "GeneralManager"):
            raise PermissionDenied("Unauthorized")
        user = self.request.user
        with transaction.atomic():
            instance = serializer.save(owner=serializer.validated_data.get("owner", user))
            try:
                editLog.objects.create(
                    user=user,
                    action="create",
                    target_model=instance.__class__.__name__,
                    target_id=instance.pk,
                    restaurant=instance,
                    before=None,
                    after=model_to_dict(instance),
                )
            except Exception as e:
                print("⚠️ editLog create failed:", e)
            return instance

    def update(self, request, *args, **kwargs):
        role = getattr(request.user, "role", None)
        if role not in ("Admin", "GeneralManager"):
            raise PermissionDenied("Unauthorized")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        before = model_to_dict(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_update(serializer)
            try:
                editLog.objects.create(
                    user=request.user,
                    action="update",
                    target_model=instance.__class__.__name__,
                    target_id=instance.pk,
                    restaurant=instance,
                    before=before,
                    after=model_to_dict(instance),
                )
            except Exception as e:
                print("⚠️ editLog update failed:", e)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        role = getattr(request.user, "role", None)
        if role != "Admin":
            raise PermissionDenied("Unauthorized")
        instance = self.get_object()
        before = model_to_dict(instance)
        with transaction.atomic():
            response = super().destroy(request, *args, **kwargs)
            try:
                editLog.objects.create(
                    user=request.user,
                    action="delete",
                    target_model=instance.__class__.__name__,
                    target_id=instance.pk,
                    restaurant=instance,
                    before=before,
                    after=None,
                )
            except Exception as e:
                print("⚠️ editLog delete failed:", e)
            return response
