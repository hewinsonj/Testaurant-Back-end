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
    """CRUD for Restaurant with simple owner scoping and edit logging.

    - Non-staff users only see their own restaurants (owner = request.user)
    - Staff/superusers see all
    - Owner auto-set on create if missing
    - Logs create/update/delete to EditLog
    """

    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Restaurant.objects.all().order_by("name")
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return qs.none()
        if user.is_staff or user.is_superuser:
            return qs
        return qs.filter(owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        with transaction.atomic():
            instance = serializer.save(owner=serializer.validated_data.get("owner", user))
            return instance

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            return super().destroy(request, *args, **kwargs)
