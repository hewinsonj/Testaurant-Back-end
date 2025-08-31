from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction
from ..models.restaurant import Restaurant
from ..models.test_this import Test_this

from ..models.result import Result
from ..serializers import ResultSerializer



# class Results(generics.ListCreateAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = ResultSerializer

#     def get(self, request):
#         results = Result.objects.all()
#         data = ResultSerializer(results, many=True).data
#         return Response({'results': data})

#     def post(self, request):
#         request.data['result']['owner'] = request.user.id
#         result = ResultSerializer(data=request.data['result'])
#         if result.is_valid():
#             result.save()
#             return Response({'result': result.data}, status=status.HTTP_201_CREATED)
#         return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)


class MyResults(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResultSerializer

    def get(self, request):
        results = Result.objects.filter(owner=request.user)
        data = ResultSerializer(results, many=True).data
        return Response({'results': data}, status=status.HTTP_200_OK)



# Create your views here.
class Results(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResultSerializer

    def get(self, request):
        role = (getattr(request.user, 'role', '') or '').lower()
        qs = Result.objects.all()
        if role == 'admin':
            results = qs
        elif role in ('generalmanager', 'manager'):
            user_rest_id = getattr(request.user, 'restaurant_id', None)
            if user_rest_id is None:
                # If the user has no restaurant, allow all results (null-tolerant on both sides)
                results = qs
            else:
                # Allow same-restaurant OR results with no restaurant set
                results = qs.filter(Q(restaurant=user_rest_id) | Q(restaurant__isnull=True))
        else:
            results = qs.filter(owner=request.user)
        data = ResultSerializer(results, many=True).data
        return Response({'results': data}, status=status.HTTP_200_OK)

    def post(self, request):
        """Create Result (role-aware, restaurant-normalized)"""
        role = (getattr(request.user, 'role', '') or '').lower()
        if role not in ('admin', 'generalmanager', 'manager', 'employee'):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        print('🛠 Incoming result data:', request.data)
        # Accept either nested {result: {...}} or a flat body
        data = request.data.get('result') or dict(request.data)
        if not isinstance(data, dict) or not data:
            return Response({'detail': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize restaurant based on role rules
        if role == 'admin':
            # Admin may set any valid restaurant id or leave it blank → None
            rest = data.get('restaurant', getattr(request.user, 'restaurant_id', None))
            if rest in ('', None):
                data['restaurant'] = None
            else:
                try:
                    rid = int(rest)
                    # Validate existence; if missing, coerce to None rather than 500
                    Restaurant.objects.only('id').get(pk=rid)
                    data['restaurant'] = rid
                except Exception:
                    data['restaurant'] = None
        else:
            # Non-admins: prefer the actor's restaurant; if none, fallback to the test's restaurant
            actor_rest_id = getattr(request.user, 'restaurant_id', None)
            if actor_rest_id is not None:
                data['restaurant'] = actor_rest_id
            else:
                test_pk = data.get('the_test')
                test_rest_id = None
                try:
                    if test_pk is not None:
                        test_obj = Test_this.objects.only('id', 'restaurant_id').get(pk=int(test_pk))
                        test_rest_id = getattr(test_obj, 'restaurant_id', None)
                except Exception:
                    test_rest_id = None
                data['restaurant'] = test_rest_id

        print('🧭 Result restaurant resolved to:', data.get('restaurant'))

        # Coerce the_test to an int if present
        if 'the_test' in data:
            try:
                data['the_test'] = int(data['the_test'])
            except Exception:
                pass

        # Owner is always the actor
        data['owner'] = request.user.id

        ser = ResultSerializer(data=data)
        if not ser.is_valid():
            print('⚠️ Result validation errors:', ser.errors)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance = ser.save()
        return Response({'result': ser.data}, status=status.HTTP_201_CREATED)

class ResultDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the result to show
        result = get_object_or_404(Result, pk=pk)
        # Only want to show owned results?
        role = (getattr(request.user, 'role', '') or '').lower()
        if role == 'admin':
            pass
        elif role in ('generalmanager', 'manager'):
            user_rest_id = getattr(request.user, 'restaurant_id', None)
            res_rest_id = result.restaurant_id
            # Only enforce mismatch when both sides have a restaurant
            if user_rest_id is not None and res_rest_id is not None and user_rest_id != res_rest_id:
                raise PermissionDenied('Unauthorized, restaurant mismatch')
        else:
            if request.user != result.owner:
                raise PermissionDenied('Unauthorized, you do not own this result')

        # Run the data through the serializer so it's formatted
        data = ResultSerializer(result).data
        return Response({ 'result': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate result to delete
        result = get_object_or_404(Result, pk=pk)
        # Check the result's owner against the user making this request
        role = (getattr(request.user, 'role', '') or '').lower()
        if role == 'admin':
            pass
        elif role == 'generalmanager':
            user_rest_id = getattr(request.user, 'restaurant_id', None)
            res_rest_id = result.restaurant_id
            if user_rest_id is not None and res_rest_id is not None and user_rest_id != res_rest_id:
                raise PermissionDenied('Unauthorized, restaurant mismatch')
        else:
            raise PermissionDenied('Unauthorized, only Admin or GeneralManager can delete results')
        # Only delete if the user owns the  result
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)