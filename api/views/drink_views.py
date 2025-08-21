from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.drink import Drink
from ..serializers import DrinkSerializer
from api.models import editLog
from django.forms.models import model_to_dict

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
                editLog.objects.create(
                    user=request.user,
                    action='create',
                    target_model=instance.__class__.__name__,
                    target_id=instance.pk,
                    restaurant=getattr(instance, 'restaurant', None),
                    before=None,
                    after=model_to_dict(instance),
                )
            except Exception as e:
                print('⚠️ editLog create failed:', e)
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
            editLog.objects.create(
                user=request.user,
                action='delete',
                target_model='Drink',
                target_id=pk,
                restaurant=getattr(request.user, 'restaurant', None),
                before=before,
                after=None,
            )
        except Exception as e:
            print('⚠️ editLog delete log failed:', e)
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
                editLog.objects.create(
                    user=request.user,
                    action='update',
                    target_model=instance.__class__.__name__,
                    target_id=instance.pk,
                    restaurant=getattr(instance, 'restaurant', None),
                    before=before,
                    after=model_to_dict(instance),
                )
            except Exception as e:
                print('⚠️ editLog update log failed:', e)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)