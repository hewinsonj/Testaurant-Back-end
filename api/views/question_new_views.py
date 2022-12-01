from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.question_new import Question_new
from ..serializers import Question_newSerializer

# Create your views here.
class Question_news(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Question_newSerializer
    def get(self, request):
        """Index request"""
        # Get all the question_news:
        question_news = Question_new.objects.all()
        # Filter the question_news by owner, so you can only see your owned question_news
        # question_news = Question_new.objects
        # Run the data through the serializer
        data = Question_newSerializer(question_news, many=True).data
        return Response({ 'question_news': data })

    def post(self, request):
        print(request.data)
        """Create request"""
        # Add user to request data object
        request.data['question_new']['owner'] = request.user.id
        # Serialize/create question_new
        question_new = Question_newSerializer(data=request.data['question_new'])
        # If the question_new data is valid according to our serializer...
        if question_new.is_valid():
            # Save the created question_new & send a response
            question_new.save()
            return Response({ 'question_new': question_new.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(question_new.errors, status=status.HTTP_400_BAD_REQUEST)

class Question_newDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the question_new to show
        question_new = get_object_or_404(Question_new, pk=pk)
        # Only want to show owned question_news?
        if request.user != question_new.owner:
            raise PermissionDenied('Unauthorized, you do not own this question_new')

        # Run the data through the serializer so it's formatted
        data = Question_newSerializer(question_new).data
        return Response({ 'question_new': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate question_new to delete
        question_new = get_object_or_404(Question_new, pk=pk)
        # Check the question_new's owner against the user making this request
        # if request.user != question_new.owner:
        #     raise PermissionDenied('Unauthorized, you do not own this question_new')
        # Only delete if the user owns the  question_new
        question_new.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Question_new
        # get_object_or_404 returns a object representation of our Question_new
        question_new = get_object_or_404(Question_new, pk=pk)
        # Check the question_new's owner against the user making this request
        if request.user != question_new.owner:
            raise PermissionDenied('Unauthorized, you do not own this question_new')

        # Ensure the owner field is set to the current user's ID
        # request.data['question_new']['owner'] = request.user.id
        # Validate updates with serializer
        data = Question_newSerializer(question_new, data=request.data['question_new'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)