from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.test_test import Test_test
from ..serializers import Test_testSerializer

# Create your views here.
class Test_tests(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Test_testSerializer
    def get(self, request):
        """Index request"""
        # Get all the test_tests:
        #test_tests = Test_test.objects.all()
        # Filter the test_tests by owner, so you can only see your owned test_tests
        test_tests = Test_test.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = Test_testSerializer(test_tests, many=True).data
        return Response({ 'test_tests': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['test_test']['owner'] = request.user.id
        # Serialize/create test_test
        test_test = Test_testSerializer(data=request.data['test_test'])
        # If the test_test data is valid according to our serializer...
        if test_test.is_valid():
            # Save the created test_test & send a response
            test_test.save()
            return Response({ 'test_test': test_test.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(test_test.errors, status=status.HTTP_400_BAD_REQUEST)

class Test_testDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the test_test to show
        test_test = get_object_or_404(Test_test, pk=pk)
        # Only want to show owned test_tests?
        if request.user != test_test.owner:
            raise PermissionDenied('Unauthorized, you do not own this test_test')

        # Run the data through the serializer so it's formatted
        data = Test_testSerializer(test_test).data
        return Response({ 'test_test': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate test_test to delete
        test_test = get_object_or_404(Test_test, pk=pk)
        # Check the test_test's owner against the user making this request
        if request.user != test_test.owner:
            raise PermissionDenied('Unauthorized, you do not own this test_test')
        # Only delete if the user owns the  test_test
        test_test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Test_test
        # get_object_or_404 returns a object representation of our Test_test
        test_test = get_object_or_404(Test_test, pk=pk)
        # Check the test_test's owner against the user making this request
        if request.user != test_test.owner:
            raise PermissionDenied('Unauthorized, you do not own this test_test')

        # Ensure the owner field is set to the current user's ID
        request.data['test_test']['owner'] = request.user.id
        # Validate updates with serializer
        data = Test_testSerializer(test_test, data=request.data['test_test'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)