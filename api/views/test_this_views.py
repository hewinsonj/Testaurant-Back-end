from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.test_this import Test_this
from ..models.question_new import Question_new
from ..serializers import Test_thisSerializer, Test_thisGetSerializer, Test_thisReadSerializer
# from ..serializers import Test_this_create_Serializer

from api.models import editLog
from django.forms.models import model_to_dict

# Create your views here.
class Test_thiss(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Test_thisSerializer
    def get(self, request):
        """Index request"""
        user = request.user
        qs = Test_this.objects.select_related('restaurant', 'owner').order_by('-updated_at')
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
        data = Test_thisGetSerializer(qs, many=True).data
        return Response({'test_thiss': data})

    def post(self, request):
        print(request.data, 'this is the dang request from post omg')
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        payload = request.data.get('test_this')
        if not payload:
            return Response({'detail': 'Missing test_this payload'}, status=status.HTTP_400_BAD_REQUEST)
        # Force associations
        if role == 'Admin':
            payload.setdefault('restaurant', getattr(request.user, 'restaurant_id', None))
        else:
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)
        payload['owner'] = request.user.id

        test_this = Test_thisSerializer(data=payload, partial=True)
        if test_this.is_valid():
            instance = test_this.save()
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
            return Response(test_this.data, status=status.HTTP_201_CREATED)
        return Response(test_this.errors, status=status.HTTP_400_BAD_REQUEST)

class Test_thisDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        test_this = get_object_or_404(Test_this, pk=pk)
        role = getattr(request.user, 'role', None)
        if role == 'Admin' or getattr(request.user, 'restaurant_id', None) == getattr(test_this, 'restaurant_id', None):
            data = Test_thisReadSerializer(test_this).data
            print(data, 'this is the dang request from get')
            return Response({'test_this': data})
        raise PermissionDenied('Unauthorized')

    def delete(self, request, pk):
        """Delete request"""
        test_this = get_object_or_404(Test_this, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(test_this, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')
        before = model_to_dict(test_this)
        test_this.delete()
        try:
            editLog.objects.create(
                user=request.user,
                action='delete',
                target_model='Test_this',
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
        test_this = get_object_or_404(Test_this, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(test_this, 'restaurant_id', None):
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