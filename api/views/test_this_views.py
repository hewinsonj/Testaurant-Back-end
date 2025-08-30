from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.test_this import Test_this
from ..models.question_new import Question_new
from ..serializers import Test_thisSerializer, Test_thisGetSerializer, Test_thisReadSerializer
# from ..serializers import Test_this_create_Serializer

from api.models.editLog import EditLog
from django.forms.models import model_to_dict

# Helper to build EditLog.changes structure


def _json_safe(val):
    """Convert non-JSON-serializable values into safe forms."""
    if isinstance(val, (str, int, float, bool)) or val is None:
        return val
    if hasattr(val, 'pk'):  # Django model instance
        return val.pk
    if isinstance(val, (list, tuple, set)):
        return [_json_safe(v) for v in val]
    if isinstance(val, dict):
        return {k: _json_safe(v) for k, v in val.items()}
    return str(val)

def _build_changes(before, after):
    try:
        before = before or {}
        after = after or {}
        keys = set(before.keys()) | set(after.keys())
        fields_changed = [k for k in keys if before.get(k) != after.get(k)]
        return {
            "before": {k: _json_safe(v) for k, v in before.items()} or None,
            "after": {k: _json_safe(v) for k, v in after.items()} or None,
            "fields_changed": fields_changed,
        }
    except Exception:
        return {"before": str(before), "after": str(after), "fields_changed": []}

# Create your views here.
class Test_thiss(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Test_thisSerializer
    def get(self, request):
        """Index request"""
        user = request.user
        qs = Test_this.objects.select_related('restaurant', 'owner').order_by('-updated_at')
        user_restaurant_id = getattr(user, 'restaurant_id', None)
        if getattr(user, 'role', None) == 'Admin':
            restaurant_id = request.query_params.get('restaurant')
            if restaurant_id:
                qs = qs.filter(restaurant=restaurant_id)
        else:
            if user_restaurant_id is None:
                qs = qs.filter(restaurant__isnull=True)
            else:
                qs = qs.filter(restaurant=user_restaurant_id)
        data = Test_thisGetSerializer(qs, many=True).data
        return Response({'test_thiss': data})

    def post(self, request):
        print(request.data, 'this is the dang request from post omg')
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        # Accept multiple shapes: {test_this: {...}}, {test: {...}}, or a flat body
        raw = request.data
        payload = raw.get('test_this') or raw.get('test') or dict(raw)
        if not isinstance(payload, dict) or not payload:
            return Response({'detail': 'Missing test payload'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize allotted_time (minutes) to an integer
        if 'allotted_time' in payload:
            try:
                payload['allotted_time'] = int(float(payload.get('allotted_time') or 0))
            except Exception:
                payload['allotted_time'] = 0

        # Force associations
        if role == 'Admin':
            # Admin may set restaurant explicitly; otherwise default to their own (which may be None)
            payload.setdefault('restaurant', getattr(request.user, 'restaurant_id', None))
        else:
            # Non-admins are locked to their restaurant, even if client sends something else
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)
        payload['owner'] = request.user.id

        ser = Test_thisSerializer(data=payload, partial=True)
        if ser.is_valid():
            instance = ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class Test_thisDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        test_this = get_object_or_404(Test_this, pk=pk)
        role = getattr(request.user, 'role', None)
        # Allow Admin always. For others, allow if restaurants match OR if BOTH are null (no restaurant on user and test).
        user_restaurant_id = getattr(request.user, 'restaurant_id', None)
        test_restaurant_id = getattr(test_this, 'restaurant_id', None)
        if role == 'Admin' or (user_restaurant_id == test_restaurant_id):
            data = Test_thisReadSerializer(test_this).data
            print(data, 'this is the dang request from get')
            return Response({'test_this': data})
        raise PermissionDenied('Unauthorized')

    def delete(self, request, pk):
        """Delete request"""
        test_this = get_object_or_404(Test_this, pk=pk)
        role = getattr(request.user, 'role', None)
        user_restaurant_id = getattr(request.user, 'restaurant_id', None)
        test_restaurant_id = getattr(test_this, 'restaurant_id', None)
        if role != 'Admin' and user_restaurant_id != test_restaurant_id:
            raise PermissionDenied('Unauthorized')
        test_this.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        test_this = get_object_or_404(Test_this, pk=pk)
        role = getattr(request.user, 'role', None)
        user_restaurant_id = getattr(request.user, 'restaurant_id', None)
        test_restaurant_id = getattr(test_this, 'restaurant_id', None)
        if role != 'Admin' and user_restaurant_id != test_restaurant_id:
            raise PermissionDenied('Unauthorized')

        payload = request.data.get('test_this') or {}
        if role != 'Admin':
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)
        payload['owner'] = request.user.id

        before = model_to_dict(test_this)
        data = Test_thisSerializer(test_this, data=payload, partial=True)
        if data.is_valid():
            instance = data.save()
            try:
                after_dict = model_to_dict(instance)
                EditLog.objects.create(
                    item_type=EditLog.ITEM_TEST,
                    item_id=instance.pk,
                    action=EditLog.ACTION_UPDATE,
                    editor=request.user,
                    restaurant=getattr(instance, 'restaurant', None),
                    item_name_snapshot=getattr(instance, 'name', '') or '',
                    editor_name_snapshot=(f"{getattr(request.user, 'first_name', '')} {getattr(request.user, 'last_name', '')}".strip() or getattr(request.user, 'email', '')),
                    changes=_build_changes(before, after_dict),
                )
            except Exception as e:
                print('⚠️ EditLog update log failed:', e)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)