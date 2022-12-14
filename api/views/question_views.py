from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.question import Question
from ..serializers import QuestionSerializer

# Create your views here.
class Questions(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = QuestionSerializer
    def get(self, request):
        """Index request"""
        # Get all the questions:
        #questions = Question.objects.all()
        # Filter the questions by owner, so you can only see your owned questions
        questions = Question.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = QuestionSerializer(questions, many=True).data
        return Response({ 'questions': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['question']['owner'] = request.user.id
        # Serialize/create question
        question = QuestionSerializer(data=request.data['question'])
        # If the question data is valid according to our serializer...
        if question.is_valid():
            # Save the created question & send a response
            question.save()
            return Response({ 'question': question.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(question.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the question to show
        question = get_object_or_404(Question, pk=pk)
        # Only want to show owned questions?
        if request.user != question.owner:
            raise PermissionDenied('Unauthorized, you do not own this question')

        # Run the data through the serializer so it's formatted
        data = QuestionSerializer(question).data
        return Response({ 'question': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate question to delete
        question = get_object_or_404(Question, pk=pk)
        # Check the question's owner against the user making this request
        if request.user != question.owner:
            raise PermissionDenied('Unauthorized, you do not own this question')
        # Only delete if the user owns the  question
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Question
        # get_object_or_404 returns a object representation of our Question
        question = get_object_or_404(Question, pk=pk)
        # Check the question's owner against the user making this request
        if request.user != question.owner:
            raise PermissionDenied('Unauthorized, you do not own this question')

        # Ensure the owner field is set to the current user's ID
        request.data['question']['owner'] = request.user.id
        # Validate updates with serializer
        data = QuestionSerializer(question, data=request.data['question'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)