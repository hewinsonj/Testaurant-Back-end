from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.quiz import Quiz
from ..serializers import QuizSerializer

# Create your views here.
class Quizs(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = QuizSerializer
    def get(self, request):
        """Index request"""
        # Get all the quizs:
        #quizs = Quiz.objects.all()
        # Filter the quizs by owner, so you can only see your owned quizs
        quizs = Quiz.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = QuizSerializer(quizs, many=True).data
        return Response({ 'quizs': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['quiz']['owner'] = request.user.id
        # Serialize/create quiz
        quiz = QuizSerializer(data=request.data['quiz'])
        # If the quiz data is valid according to our serializer...
        if quiz.is_valid():
            # Save the created quiz & send a response
            quiz.save()
            return Response({ 'quiz': quiz.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(quiz.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the quiz to show
        quiz = get_object_or_404(Quiz, pk=pk)
        # Only want to show owned quizs?
        if request.user != quiz.owner:
            raise PermissionDenied('Unauthorized, you do not own this quiz')

        # Run the data through the serializer so it's formatted
        data = QuizSerializer(quiz).data
        return Response({ 'quiz': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate quiz to delete
        quiz = get_object_or_404(Quiz, pk=pk)
        # Check the quiz's owner against the user making this request
        if request.user != quiz.owner:
            raise PermissionDenied('Unauthorized, you do not own this quiz')
        # Only delete if the user owns the  quiz
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Quiz
        # get_object_or_404 returns a object representation of our Quiz
        quiz = get_object_or_404(Quiz, pk=pk)
        # Check the quiz's owner against the user making this request
        if request.user != quiz.owner:
            raise PermissionDenied('Unauthorized, you do not own this quiz')

        # Ensure the owner field is set to the current user's ID
        request.data['quiz']['owner'] = request.user.id
        # Validate updates with serializer
        data = QuizSerializer(quiz, data=request.data['quiz'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)