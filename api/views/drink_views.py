from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from django.shortcuts import get_object_or_404

from ..models.drink import Drink
from ..serializers import DrinkSerializer

# Create your views here.
class Drinks(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = DrinkSerializer
    def get(self, request):
        """Index request"""
        # Get all the drinks:
        drinks = Drink.objects.all()
        # Filter the drinks by owner, so you can only see your owned drinks
        # drinks = Drink.objects.filter(owner=request.user.id)
        # Run the data through the serializer
        data = DrinkSerializer(drinks, many=True).data
        return Response({ 'drinks': data })

    def post(self, request):
        """Create request"""
        # Add user to request data object
        request.data['drink']['owner'] = request.user.id
        # Serialize/create drink
        drink = DrinkSerializer(data=request.data['drink'])
        # If the drink data is valid according to our serializer...
        if drink.is_valid():
            # Save the created drink & send a response
            drink.save()
            return Response({ 'drink': drink.data }, status=status.HTTP_201_CREATED)
        # If the data is not valid, return a response with the errors
        return Response(drink.errors, status=status.HTTP_400_BAD_REQUEST)

class DrinkDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def get(self, request, pk):
        """Show request"""
        # Locate the drink to show
        drink = get_object_or_404(Drink, pk=pk)
        # Only want to show owned drinks?
        if request.user != drink.owner:
            raise PermissionDenied('Unauthorized, you do not own this drink')

        # Run the data through the serializer so it's formatted
        data = DrinkSerializer(drink).data
        return Response({ 'drink': data })

    def delete(self, request, pk):
        """Delete request"""
        # Locate drink to delete
        drink = get_object_or_404(Drink, pk=pk)
        # Check the drink's owner against the user making this request
        if request.user != drink.owner:
            raise PermissionDenied('Unauthorized, you do not own this drink')
        # Only delete if the user owns the  drink
        drink.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk):
        """Update Request"""
        # Locate Drink
        # get_object_or_404 returns a object representation of our Drink
        drink = get_object_or_404(Drink, pk=pk)
        # Check the drink's owner against the user making this request
        if request.user != drink.owner:
            raise PermissionDenied('Unauthorized, you do not own this drink')

        # Ensure the owner field is set to the current user's ID
        request.data['drink']['owner'] = request.user.id
        # Validate updates with serializer
        data = DrinkSerializer(drink, data=request.data['drink'], partial=True)
        if data.is_valid():
            # Save & send a 204 no content
            data.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # If the data is not valid, return a response with the errors
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)