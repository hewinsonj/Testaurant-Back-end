from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import editLog
from api.serializers import EditLogSerializer
from api.permissions import IsAdminOrRestaurantManager

# NOTE: Keep this un-routed externally. Logs should be server-generated (mixins/signals), not client POSTed.
@api_view(['POST'])
def log_edit(request, action, instance, before=None, after=None):
    editLog.objects.create(
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
        # Optimize FK access and enforce role + restaurant scoping
        qs = editLog.objects.select_related('restaurant', 'user').order_by('-editDate')
        role = getattr(user, 'role', None)
        if role == 'Admin':
            return qs
        if role in ('GeneralManager', 'Manager'):
            return qs.filter(restaurant=getattr(user, 'restaurant_id', None))
        # Employees and others: no access
        return qs.none()
