from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

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
            results = qs.filter(restaurant=getattr(request.user, 'restaurant_id', None))
        else:
            results = qs.filter(owner=request.user)
        data = ResultSerializer(results, many=True).data
        return Response({'results': data}, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        """Create request"""
        # Add user to request data object
        request.data['result']['owner'] = request.user.id
        # Serialize/create result
        result = ResultSerializer(data=request.data['result'])
        # If the result data is valid according to our serializer...
        if result.is_valid():
            # Save the created result & send a response
            result.save()
            return Response({ 'result': result.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)

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
            if result.restaurant_id != getattr(request.user, 'restaurant_id', None):
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
            if result.restaurant_id != getattr(request.user, 'restaurant_id', None):
                raise PermissionDenied('Unauthorized, restaurant mismatch')
        else:
            raise PermissionDenied('Unauthorized, only Admin or GeneralManager can delete results')
        # Only delete if the user owns the  result
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)