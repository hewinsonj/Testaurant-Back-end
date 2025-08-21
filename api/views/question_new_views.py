from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.question_new import Question_new
from ..serializers import Question_newSerializer
from api.models import editLog
from django.forms.models import model_to_dict

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
        payload = request.data.get('question_new')
        if not payload:
            return Response({'detail': 'Missing question_new payload'}, status=status.HTTP_400_BAD_REQUEST)

        if role == 'Admin':
            payload.setdefault('restaurant', getattr(request.user, 'restaurant_id', None))
        else:
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)

        serializer = Question_newSerializer(data=payload)
        if serializer.is_valid():
            instance = serializer.save(owner=request.user)
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
            return Response({'question_new': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Question_newDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        question_new = get_object_or_404(Question_new, pk=pk)
        role = getattr(request.user, 'role', None)
        if role == 'Admin' or getattr(request.user, 'restaurant_id', None) == getattr(question_new, 'restaurant_id', None):
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
        before = model_to_dict(question_new)
        question_new.delete()
        try:
            editLog.objects.create(
                user=request.user,
                action='delete',
                target_model='Question_new',
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
        question_new = get_object_or_404(Question_new, pk=pk)
        role = getattr(request.user, 'role', None)
        if role not in ('Admin', 'GeneralManager', 'Manager'):
            raise PermissionDenied('Unauthorized')
        if role != 'Admin' and getattr(request.user, 'restaurant_id', None) != getattr(question_new, 'restaurant_id', None):
            raise PermissionDenied('Unauthorized')

        payload = request.data.get('question_new') or {}
        if role != 'Admin':
            payload['restaurant'] = getattr(request.user, 'restaurant_id', None)
        payload['owner'] = request.user.id

        before = model_to_dict(question_new)
        data = Question_newSerializer(question_new, data=payload, partial=True)
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