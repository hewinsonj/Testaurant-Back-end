from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.drink import Drink
from ..serializers import DrinkSerializer
from api.models.editLog import EditLog
from django.forms.models import model_to_dict

# Helper to build EditLog.changes structure
from django.forms.models import model_to_dict

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
class Drinks(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = DrinkSerializer
    def get(self, request):
        """Index request"""
        user = request.user
        qs = Drink.objects.select_related('restaurant', 'owner').order_by('-updated_at')
        role = getattr(user, 'role', None)
        if role == 'Admin':
            # Admin can optionally filter by restaurant via query param
            restaurant_id = request.query_params.get('restaurant')
            if restaurant_id:
                qs = qs.filter(restaurant=restaurant_id)
        elif role in ('GeneralManager', 'Manager'):
            qs = qs.filter(restaurant=getattr(user, 'restaurant_id', None))
        else:
            # Employees: allow read if restaurant matches
            qs = qs.filter(restaurant=getattr(user, 'restaurant_id', None))
        data = DrinkSerializer(qs, many=True).data
        return Response({'drinks': data})

    def post(self, request):
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        print("🛠 Incoming drink data:", request.data)
        drink_data = request.data.get('drink')
        if not drink_data:
            return Response({'detail': 'Missing drink payload'}, status=status.HTTP_400_BAD_REQUEST)

        # Force restaurant based on actor unless Admin explicitly sets one
        if role == 'Admin':
            drink_data.setdefault('restaurant', getattr(request.user, 'restaurant_id', None))
        else:
            drink_data['restaurant'] = getattr(request.user, 'restaurant_id', None)

        serializer = DrinkSerializer(data=drink_data)
        if serializer.is_valid():
            instance = serializer.save(owner=request.user)
            # Best-effort audit log
            try:
                EditLog.objects.create(
                    item_type=EditLog.ITEM_DRINK,
                    item_id=instance.pk,
                    action=EditLog.ACTION_CREATE,
                    editor=request.user,
                    restaurant=getattr(instance, 'restaurant', None),
                    item_name_snapshot=getattr(instance, 'name', '') or '',
                    editor_name_snapshot=(f"{getattr(request.user, 'first_name', '')} {getattr(request.user, 'last_name', '')}".strip() or getattr(request.user, 'email', '')),
                    changes=_build_changes(None, model_to_dict(instance)),
                )
            except Exception as e:
                print('⚠️ EditLog create failed:', e)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("❌ Drink creation error:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DrinkDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        drink = get_object_or_404(Drink, pk=pk)
        role = getattr(request.user, 'role', None)
        if role == 'Admin' or getattr(request.user, 'restaurant_id', None) == getattr(drink, 'restaurant_id', None):
            data = DrinkSerializer(drink).data
            return Response({'drink': data})
        raise PermissionDenied('Unauthorized')

    def delete(self, request, pk):
        """Delete request"""
        drink = get_object_or_404(Drink, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(drink, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')
        before = model_to_dict(drink)
        drink.delete()
        try:
            EditLog.objects.create(
                item_type=EditLog.ITEM_DRINK,
                item_id=pk,
                action=EditLog.ACTION_DELETE,
                editor=request.user,
                restaurant=getattr(request.user, 'restaurant', None),
                item_name_snapshot=str(before.get('name') or ''),
                editor_name_snapshot=(f"{getattr(request.user, 'first_name', '')} {getattr(request.user, 'last_name', '')}".strip() or getattr(request.user, 'email', '')),
                changes=_build_changes(before, None),
            )
        except Exception as e:
            print('⚠️ EditLog delete log failed:', e)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        drink = get_object_or_404(Drink, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(drink, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')

        payload = request.data.get('drink') or {}
        # Lock restaurant for non-admins
        if role != 'Admin':
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)
        # Always preserve owner as the actor
        payload['owner'] = request.user.id

        before = model_to_dict(drink)
        data = DrinkSerializer(drink, data=payload, partial=True)
        if data.is_valid():
            instance = data.save()
            try:
                after_dict = model_to_dict(instance)
                EditLog.objects.create(
                    item_type=EditLog.ITEM_DRINK,
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