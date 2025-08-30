from api.models import editLog
from django.forms.models import model_to_dict
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import transaction
from ..models.restaurant import Restaurant

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
    - Logs only PATCH updates to editLog.
    """

    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Restaurant.objects.all().order_by("name")
        user = getattr(self.request, "user", None)
        # Allow unauthenticated users to see the list (SignUp needs it)
        if not user or not user.is_authenticated:
            return qs
        role = getattr(user, "role", None)
        if role in ("Admin", "GeneralManager", "Manager"):
            return qs
        # Employees: also return all per your last change
        return qs

    def perform_create(self, serializer):
        role = getattr(self.request.user, "role", None)
        if role not in ("Admin", "GeneralManager"):
            raise PermissionDenied("Unauthorized")
        user = self.request.user
        with transaction.atomic():
            instance = serializer.save(owner=serializer.validated_data.get("owner", user))
            return instance

    def create(self, request, *args, **kwargs):
        role = getattr(request.user, "role", None)
        if role not in ("Admin", "GeneralManager", "Manager"):
            raise PermissionDenied("Unauthorized")

        # Accept both flat payloads and nested {"restaurant": {...}}
        payload = request.data.get("restaurant", request.data)
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        user = request.user
        with transaction.atomic():
            instance = serializer.save(owner=payload.get("owner", user))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        role = getattr(request.user, "role", None)
        if role not in ("Admin", "GeneralManager", "Manager"):
            raise PermissionDenied("Unauthorized")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        before = model_to_dict(instance)
        payload = request.data.get("restaurant", request.data)
        serializer = self.get_serializer(instance, data=payload, partial=partial)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_update(serializer)
            if partial:
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
        with transaction.atomic():
            response = super().destroy(request, *args, **kwargs)
            return response
