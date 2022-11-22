from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.food import Food
from ..serializers import FoodSerializer

# Create your views here.
class Foods(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = FoodSerializer
    def get(self, request):
        """Index request"""
        # Get all the foods:
        # foods = Food.objects.all()
        # Filter the foods by owner, so you can only see your owned foods
        foods = Food.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = FoodSerializer(foods, many=True).data
        return Response({ 'foods': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['food']['owner'] = request.user.id
        # Serialize/create food
        food = FoodSerializer(data=request.data['food'])
        # If the food data is valid according to our serializer...
        if food.is_valid():
            # Save the created food & send a response
            food.save()
            return Response({ 'food': food.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(food.errors, status=status.HTTP_400_BAD_REQUEST)

class FoodDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the food to show
        food = get_object_or_404(Food, pk=pk)
        # Only want to show owned foods?
        if request.user != food.owner:
            raise PermissionDenied('Unauthorized, you do not own this food')

        # Run the data through the serializer so it's formatted
        data = FoodSerializer(food).data
        return Response({ 'food': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate food to delete
        food = get_object_or_404(Food, pk=pk)
        # Check the food's owner against the user making this request
        if request.user != food.owner:
            raise PermissionDenied('Unauthorized, you do not own this food')
        # Only delete if the user owns the  food
        food.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Food
        # get_object_or_404 returns a object representation of our Food
        food = get_object_or_404(Food, pk=pk)
        # Check the food's owner against the user making this request
        if request.user != food.owner:
            raise PermissionDenied('Unauthorized, you do not own this food')

        # Ensure the owner field is set to the current user's ID
        request.data['food']['owner'] = request.user.id
        # Validate updates with serializer
        data = FoodSerializer(food, data=request.data['food'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)