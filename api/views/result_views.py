from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.result import Result
from ..serializers import ResultSerializer

# Create your views here.
class Results(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = ResultSerializer
    def get(self, request):
        """Index request"""
        # Get all the results:
        results = Result.objects.all()
        # Filter the results by owner, so you can only see your owned results
        # results = Result.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = ResultSerializer(results, many=True).data
        return Response({ 'results': data })

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
        if request.user != result.owner:
            raise PermissionDenied('Unauthorized, you do not own this result')
        # Only delete if the user owns the  result
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Result
        # get_object_or_404 returns a object representation of our Result
        result = get_object_or_404(Result, pk=pk)
        # Check the result's owner against the user making this request
        # if request.user != result.owner:
        #     raise PermissionDenied('Unauthorized, you do not own this result')

        # Ensure the owner field is set to the current user's ID
        request.data['result']['owner'] = request.user.id
        # Validate updates with serializer
        data = ResultSerializer(result, data=request.data['result'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)