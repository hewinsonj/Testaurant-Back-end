from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.test_many import Test_many
from ..serializers import Test_manySerializer

# Create your views here.
class Test_manys(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = Test_manySerializer
    def get(self, request):
        """Index request"""
        # Get all the test_manys:
        #test_manys = Test_many.objects.all()
        # Filter the test_manys by owner, so you can only see your owned test_manys
        test_manys = Test_many.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = Test_manySerializer(test_manys, many=True).data
        return Response({ 'test_manys': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['test_many']['owner'] = request.user.id
        # Serialize/create test_many
        test_many = Test_manySerializer(data=request.data['test_many'])
        # If the test_many data is valid according to our serializer...
        if test_many.is_valid():
            # Save the created test_many & send a response
            test_many.save()
            return Response({ 'test_many': test_many.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(test_many.errors, status=status.HTTP_400_BAD_REQUEST)

class Test_manyDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the test_many to show
        test_many = get_object_or_404(Test_many, pk=pk)
        # Only want to show owned test_manys?
        if request.user != test_many.owner:
            raise PermissionDenied('Unauthorized, you do not own this test_many')

        # Run the data through the serializer so it's formatted
        data = Test_manySerializer(test_many).data
        return Response({ 'test_many': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate test_many to delete
        test_many = get_object_or_404(Test_many, pk=pk)
        # Check the test_many's owner against the user making this request
        if request.user != test_many.owner:
            raise PermissionDenied('Unauthorized, you do not own this test_many')
        # Only delete if the user owns the  test_many
        test_many.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Test_many
        # get_object_or_404 returns a object representation of our Test_many
        test_many = get_object_or_404(Test_many, pk=pk)
        # Check the test_many's owner against the user making this request
        if request.user != test_many.owner:
            raise PermissionDenied('Unauthorized, you do not own this test_many')

        # Ensure the owner field is set to the current user's ID
        request.data['test_many']['owner'] = request.user.id
        # Validate updates with serializer
        data = Test_manySerializer(test_many, data=request.data['test_many'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)