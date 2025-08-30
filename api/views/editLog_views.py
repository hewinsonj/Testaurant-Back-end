from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from api.models.editLog import EditLog
from api.serializers import EditLogSerializer
from api.permissions import IsAdminOrRestaurantManager

# NOTE: Keep this un-routed externally. Logs should be server-generated (mixins/signals), not client POSTed.
@api_view(['POST'])
def log_edit(request, action, instance, before=None, after=None):
    EditLog.objects.create(
        user=request.user,
        action=action,
        instance=instance,
        before=before,
        after=after
    )
    return Response({"status": "edit logged"})


# ReadOnly ViewSet for EditLog
class EditLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrRestaurantManager]
    serializer_class = EditLogSerializer

    def get_queryset(self):
        user = self.request.user
        qs = EditLog.objects.select_related('restaurant', 'editor')
        # Prefer created_at if available, otherwise fall back
        try:
            qs = qs.order_by('-created_at')
        except Exception:
            try:
                qs = qs.order_by('-editDate')
            except Exception:
                qs = qs.order_by('-id')

        role = getattr(user, 'role', None)
        if role == 'Admin':
            return qs
        if role in ('GeneralManager', 'Manager'):
            user_restaurant_id = getattr(user, 'restaurant_id', None)
            if user_restaurant_id is None:
                # Manager/GM without a restaurant: only logs with no restaurant
                return qs.filter(restaurant__isnull=True)
            # Otherwise: logs for their restaurant OR logs with no restaurant
            return qs.filter(Q(restaurant_id=user_restaurant_id) | Q(restaurant__isnull=True))
        # Employees and others: no access
        return qs.none()
