from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.quiz_test import Quiz_test
from ..serializers import Quiz_testSerializer

# Create your views here.
class Quiz_tests(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Quiz_testSerializer
    def get(self, request):
        """Index request"""
        # Get all the quiz_tests:
        #quiz_tests = Quiz_test.objects.all()
        # Filter the quiz_tests by owner, so you can only see your owned quiz_tests
        quiz_tests = Quiz_test.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = Quiz_testSerializer(quiz_tests, many=True).data
        return Response({ 'quiz_tests': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['quiz_test']['owner'] = request.user.id
        # Serialize/create quiz_test
        quiz_test = Quiz_testSerializer(data=request.data['quiz_test'])
        # If the quiz_test data is valid according to our serializer...
        if quiz_test.is_valid():
            # Save the created quiz_test & send a response
            quiz_test.save()
            return Response({ 'quiz_test': quiz_test.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(quiz_test.errors, status=status.HTTP_400_BAD_REQUEST)

class Quiz_testDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the quiz_test to show
        quiz_test = get_object_or_404(Quiz_test, pk=pk)
        # Only want to show owned quiz_tests?
        if request.user != quiz_test.owner:
            raise PermissionDenied('Unauthorized, you do not own this quiz_test')

        # Run the data through the serializer so it's formatted
        data = Quiz_testSerializer(quiz_test).data
        return Response({ 'quiz_test': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate quiz_test to delete
        quiz_test = get_object_or_404(Quiz_test, pk=pk)
        # Check the quiz_test's owner against the user making this request
        if request.user != quiz_test.owner:
            raise PermissionDenied('Unauthorized, you do not own this quiz_test')
        # Only delete if the user owns the  quiz_test
        quiz_test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Quiz_test
        # get_object_or_404 returns a object representation of our Quiz_test
        quiz_test = get_object_or_404(Quiz_test, pk=pk)
        # Check the quiz_test's owner against the user making this request
        if request.user != quiz_test.owner:
            raise PermissionDenied('Unauthorized, you do not own this quiz_test')

        # Ensure the owner field is set to the current user's ID
        request.data['quiz_test']['owner'] = request.user.id
        # Validate updates with serializer
        data = Quiz_testSerializer(quiz_test, data=request.data['quiz_test'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)