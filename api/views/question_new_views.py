from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.question_new import Question_new
from ..models.restaurant import Restaurant
from ..serializers import Question_newSerializer
from api.models.editLog import EditLog
from django.forms.models import model_to_dict

# Helper to build EditLog.changes structure
def _build_changes(before, after):
    try:
        before = before or {}
        after = after or {}
        keys = set(before.keys()) | set(after.keys())
        fields_changed = [k for k in keys if before.get(k) != after.get(k)]
        return {
            "before": before or None,
            "after": after or None,
            "fields_changed": fields_changed,
        }
    except Exception:
        return {"before": before, "after": after, "fields_changed": []}

# Create your views here.
class Question_news(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Question_newSerializer
    def get(self, request):
        """Index request"""
        user = request.user
        qs = Question_new.objects.select_related('restaurant', 'owner').order_by('-updated_at')
        role = getattr(user, 'role', None)
        if role == 'Admin':
            restaurant_id = request.query_params.get('restaurant')
            if restaurant_id:
                qs = qs.filter(restaurant=restaurant_id)
        elif role in ('GeneralManager', 'Manager'):
            qs = qs.filter(restaurant=getattr(user, 'restaurant_id', None))
        else:
            # Employees: allow read if restaurant matches
            qs = qs.filter(restaurant=getattr(user, 'restaurant_id', None))
        data = Question_newSerializer(qs, many=True).data
        return Response({'question_news': data})

    def post(self, request):
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        print("🛠 Incoming question_new data:", request.data)
        # Accept either {question_new: {...}} or a flat body
        payload = request.data.get('question_new') or dict(request.data)
        if not isinstance(payload, dict) or not payload:
            return Response({'detail': 'Missing question_new payload'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize restaurant based on role
        if role == 'Admin':
            # Admin may set any valid restaurant id, or clear it to None
            if 'restaurant' in payload:
                rest = payload.get('restaurant')
                if rest in ('', None):
                    payload['restaurant'] = None
                else:
                    try:
                        rid = int(rest)
                        # Validate existence for a clearer error than a generic 400
                        get_object_or_404(Restaurant, pk=rid)
                        payload['restaurant'] = rid
                    except Exception:
                        payload['restaurant'] = None
            else:
                # Default to the actor's restaurant (which may be None)
                payload.setdefault('restaurant', getattr(request.user, 'restaurant_id', None))
        else:
            # Non-admins are locked to their own restaurant
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)

        serializer = Question_newSerializer(data=payload)
        if serializer.is_valid():
            instance = serializer.save(owner=request.user)
            return Response({'question_new': serializer.data}, status=status.HTTP_201_CREATED)

        # Log validation errors to help diagnose 400s
        print('⚠️ Question_new validation errors:', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Question_newDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        question_new = get_object_or_404(Question_new, pk=pk)
        role = getattr(request.user, 'role', None)
        user_restaurant_id = getattr(request.user, 'restaurant_id', None)
        question_restaurant_id = getattr(question_new, 'restaurant_id', None)

        # Allow Admin always.
        # For others, allow if restaurants match OR if the question has no restaurant assigned.
        if (
            role == 'Admin'
            or question_restaurant_id is None
            or user_restaurant_id == question_restaurant_id
        ):
            data = Question_newSerializer(question_new).data
            return Response({'question_new': data})
        raise PermissionDenied('Unauthorized')

    def delete(self, request, pk):
        """Delete request"""
        question_new = get_object_or_404(Question_new, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(question_new, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')
        question_new.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        question_new = get_object_or_404(Question_new, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(question_new, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')
        print("🛠 Incoming question_new data:", request.data)

        payload = request.data.get('question_new') or {}

        if role == 'Admin':
            if 'restaurant' in payload:
                rest = payload.get('restaurant')
                if rest in ('', None):
                    payload['restaurant'] = None
                else:
                    try:
                        rid = int(rest)
                        get_object_or_404(Restaurant, pk=rid)
                        payload['restaurant'] = rid
                    except Exception:
                        payload['restaurant'] = None
        else:
            # Lock restaurant for non-admins
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)

        # Always preserve owner as the actor
        payload['owner'] = request.user.id

        before = model_to_dict(question_new)
        data = Question_newSerializer(question_new, data=payload, partial=True)
        if data.is_valid():
            instance = data.save()
            # Only log for PATCH (partial updates)
            if True:  # partial is always True here
                try:
                    after_dict = model_to_dict(instance)
                    EditLog.objects.create(
                        item_type=EditLog.ITEM_QUESTION,
                        item_id=instance.pk,
                        action=EditLog.ACTION_UPDATE,
                        editor=request.user,
                        restaurant=getattr(instance, 'restaurant', None),
                        item_name_snapshot=getattr(instance, 'question_str', '') or '',
                        editor_name_snapshot=(f"{getattr(request.user, 'first_name', '')} {getattr(request.user, 'last_name', '')}".strip() or getattr(request.user, 'email', '')),
                        changes=_build_changes(before, after_dict),
                    )
                except Exception as e:
                    print('⚠️ EditLog update log failed:', e)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)