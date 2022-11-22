from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.test import Test
from ..serializers import TestSerializer

# Create your views here.
class Tests(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = TestSerializer
    def get(self, request):
        """Index request"""
        # Get all the tests:
        #tests = Test.objects.all()
        # Filter the tests by owner, so you can only see your owned tests
        tests = Test.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = TestSerializer(tests, many=True).data
        return Response({ 'tests': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['test']['owner'] = request.user.id
        # Serialize/create test
        test = TestSerializer(data=request.data['test'])
        # If the test data is valid according to our serializer...
        if test.is_valid():
            # Save the created test & send a response
            test.save()
            return Response({ 'test': test.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(test.errors, status=status.HTTP_400_BAD_REQUEST)

class TestDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the test to show
        test = get_object_or_404(Test, pk=pk)
        # Only want to show owned tests?
        if request.user != test.owner:
            raise PermissionDenied('Unauthorized, you do not own this test')

        # Run the data through the serializer so it's formatted
        data = TestSerializer(test).data
        return Response({ 'test': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate test to delete
        test = get_object_or_404(Test, pk=pk)
        # Check the test's owner against the user making this request
        if request.user != test.owner:
            raise PermissionDenied('Unauthorized, you do not own this test')
        # Only delete if the user owns the  test
        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Test
        # get_object_or_404 returns a object representation of our Test
        test = get_object_or_404(Test, pk=pk)
        # Check the test's owner against the user making this request
        if request.user != test.owner:
            raise PermissionDenied('Unauthorized, you do not own this test')

        # Ensure the owner field is set to the current user's ID
        request.data['test']['owner'] = request.user.id
        # Validate updates with serializer
        data = TestSerializer(test, data=request.data['test'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)