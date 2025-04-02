from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user, authenticate, login, logout
from rest_framework.authtoken.models import Token


from ..serializers import UserSerializer, UserRegisterSerializer,  ChangePasswordSerializer
from ..models.user import User

class SignUp(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            data.pop('password_confirmation')

            # Create the user
            user = User.objects.create_user(**data)

            # Create or retrieve token
            token, _ = Token.objects.get_or_create(user=user)

            # Serialize user and attach token to response
            serialized_user = UserSerializer(user).data
            serialized_user['token'] = token.key

            return Response({'user': serialized_user}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignIn(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        creds = request.data
        user = authenticate(request, email=creds.get('email'), password=creds.get('password'))

        if user is not None and user.is_active:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            serialized_user = UserSerializer(user).data
            serialized_user['token'] = token.key  # ✅ Attach the token directly to user object

            return Response({
                'user': serialized_user
            }, status=status.HTTP_200_OK)

        return Response(
            {'msg': 'Invalid credentials or inactive account'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class SignOut(generics.DestroyAPIView):
    def delete(self, request):
        # Remove this token from the user
        request.user.delete_token()
        # Logout will remove all session data
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangePassword(generics.UpdateAPIView):
    def partial_update(self, request):
        user = request.user
        # Pass data through serializer
        serializer = ChangePasswordSerializer(data=request.data['passwords'])
        if serializer.is_valid():
            # This is included with the Django base user model
            # https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#django.contrib.auth.models.User.check_password
            if not user.check_password(serializer.data['old']):
                return Response({ 'msg': 'Wrong password' }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            # set_password will also hash the password
            # https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#django.contrib.auth.models.User.set_password
            user.set_password(serializer.data['new'])
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Users(generics.ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class = UserSerializer
    def get(self, request):
        """Index request"""
        # Get all the test_thiss:
        users = User.objects.all()
        # Filter the test_thiss by owner, so you can only see your owned test_thiss
        # test_thiss = Test_this.objects
        # Run the data through the serializer
        data = UserSerializer(users, many=True).data
        return Response({ 'users': data })
    
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()