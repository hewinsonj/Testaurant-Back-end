from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.food import Food
from ..serializers import FoodSerializer
from api.models import editLog
from django.forms.models import model_to_dict

# Create your views here.
class Foods(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = FoodSerializer
    def get(self, request):
        """Index request"""
        user = request.user
        qs = Food.objects.select_related('restaurant', 'owner').order_by('-updated_at')
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
        data = FoodSerializer(qs, many=True).data
        return Response({'foods': data})

    def post(self, request):
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        print("🛠 Incoming food data:", request.data)
        food_data = request.data.get('food')
        if not food_data:
            return Response({'detail': 'Missing food payload'}, status=status.HTTP_400_BAD_REQUEST)

        # Force restaurant based on actor unless Admin explicitly sets one
        if role == 'Admin':
            # allow provided restaurant or default to user's restaurant
            food_data.setdefault('restaurant', getattr(request.user, 'restaurant_id', None))
        else:
            food_data['restaurant'] = getattr(request.user, 'restaurant_id', None)

        serializer = FoodSerializer(data=food_data)
        if serializer.is_valid():
            instance = serializer.save(owner=request.user)
            # Try to write an edit log; do not fail the request if logging fails
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
            print("❌ Food creation error:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class FoodDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        food = get_object_or_404(Food, pk=pk)
        role = getattr(request.user, 'role', None)
        if role == 'Admin' or getattr(request.user, 'restaurant_id', None) == getattr(food, 'restaurant_id', None):
            data = FoodSerializer(food).data
            return Response({'food': data})
        raise PermissionDenied('Unauthorized')

    def delete(self, request, pk):
        """Delete request"""
        food = get_object_or_404(Food, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(food, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')
        before = model_to_dict(food)
        food.delete()
        try:
            editLog.objects.create(
                user=request.user,
                action='delete',
                target_model='Food',
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
        food = get_object_or_404(Food, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(food, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')

        payload = request.data.get('food') or {}
        # Lock restaurant for non-admins
        if role != 'Admin':
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)
        # Always preserve owner as the actor
        payload['owner'] = request.user.id

        before = model_to_dict(food)
        data = FoodSerializer(food, data=payload, partial=True)
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