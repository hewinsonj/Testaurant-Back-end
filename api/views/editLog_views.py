from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import EditLog
from api.serializers import EditLogSerializer

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
    queryset = EditLog.objects.all().order_by('-editDate')
    serializer_class = EditLogSerializer

    def get_queryset(self):
        # Temporary role-based check; will later be updated to enforce restaurant-based scoping for more secure authorization
        user = self.request.user
        if user.role in ["Admin", "GeneralManager", "Manager"]:
            return EditLog.objects.all().order_by('-editDate')
        else:
            return EditLog.objects.filter(user=user).order_by('-editDate')
