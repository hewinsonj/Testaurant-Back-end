from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.test_this import Test_this
from ..serializers import Test_thisSerializer
# from ..serializers import Test_this_create_Serializer

# Create your views here.
class Test_thiss(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Test_thisSerializer
    def get(self, request):
        """Index request"""
        # Get all the test_thiss:
        test_thiss = Test_this.objects.all()
        # Filter the test_thiss by owner, so you can only see your owned test_thiss
        # test_thiss = Test_this.objects
        # Run the data through the serializer
        data = Test_thisSerializer(test_thiss, many=True).data
        return Response({ 'test_thiss': data })

    def post(self, request):
        print(request.data)
        """Create request"""
        # Add user to request data object
        request.data['test_this']['owner'] = request.user.id
        # Serialize/create test_this
        # temp_question_arr = request.data['test_this']['question_new']

        # print(temp_question_arr, 'This is the temp q arr')
        # request.data['test_this']['question_new'] = []
        test_this = Test_thisSerializer(data=request.data['test_this'])
        # print(test_this, 'This is after the serializer')
        # If the test_this data is valid according to our serializer...
        if test_this.is_valid():
            print('First test')
            # Save the created test_this & send a response
            test_this.save()
            # test_this.save_m2m()
            # print('Second Test')
            # for question in temp_question_arr:
            #     # test_this.question_new = []
            #     test_this['question_new'].add(question)            
            # print('Third Test')
            # test_this.save()
            # test_this['question_new'] = temp_question_arr
            # test_this.save()
            # print(test_this.question_new, 'this is the test after the reassignment from temp')
            return Response({ 'test_this': test_this.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(test_this.errors, status=status.HTTP_400_BAD_REQUEST)

class Test_thisDetail(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the test_this to show
        test_this = get_object_or_404(Test_this, pk=pk)
        # Only want to show owned test_thiss?
        # if request.user != test_this.owner:
        #     raise PermissionDenied('Unauthorized, you do not own this test_this')

        # Run the data through the serializer so it's formatted
        data = Test_thisSerializer(test_this).data
        return Response({ 'test_this': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate test_this to delete
        test_this = get_object_or_404(Test_this, pk=pk)
        # Check the test_this's owner against the user making this request
        # if request.user != test_this.owner:
        #     raise PermissionDenied('Unauthorized, you do not own this test_this')
        # Only delete if the user owns the  test_this
        test_this.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Test_this
        # get_object_or_404 returns a object representation of our Test_this
        test_this = get_object_or_404(Test_this, pk=pk)
        # Check the test_this's owner against the user making this request
        if request.user != test_this.owner:
            raise PermissionDenied('Unauthorized, you do not own this test_this')

        # Ensure the owner field is set to the current user's ID
        request.data['test_this']['owner'] = request.user.id
        # Validate updates with serializer
        data = Test_thisSerializer(test_this, data=request.data['test_this'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)