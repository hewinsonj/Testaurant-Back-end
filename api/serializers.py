from django.contrib.auth import get_user_model
from rest_framework import serializers


from .models.question_new import Question_new
from .models.user import User
from .models.food import Food
from .models.drink import Drink
from .models.result import Result
from .models.test_this import Test_this

class Question_newSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Question_new

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Food
    
# class Test_thisSerializer(serializers.ModelSerializer):
#     question_new = Question_newSerializer(many=True, read_only=True)
#     class Meta:
#         model = Test_this
#         fields = ('name', 'question_new', 'owner', 'created_at', 'updated_at', 'id')
#     def create(self, validated_data):
#         # question_new_data = validated_data.pop('question_new')
#         test_this = Test_this.objects.create(**validated_data)
#         # for question_new_data in question_new_data:
#         #     Question_new.objects.create(test_this=test_this, **question_new_data)
#         return test_this

class Test_thisSerializer(serializers.ModelSerializer):
    # Allow the frontend to send a list of `question_new` IDs
    question_new = serializers.PrimaryKeyRelatedField(
        queryset=Question_new.objects.all(),
        many=True
    )

    class Meta:
        model = Test_this
        fields = ('name', 'question_new', 'owner', 'created_at', 'updated_at', 'id')

    def create(self, validated_data):
        # Extract `question_new` data (list of IDs)
        question_new_data = validated_data.pop('question_new', [])
        
        # Create the `Test_this` object
        test_this = Test_this.objects.create(**validated_data)
        
        # Assign the many-to-many relationship
        test_this.question_new.set(question_new_data)
        
        return test_this

class Test_thisReadSerializer(serializers.ModelSerializer):
    question_new = serializers.StringRelatedField(many=True)
    class Meta:
        fields = '__all__'
        model = Test_this

class Test_thisGetSerializer(serializers.ModelSerializer):
    question_new = Question_newSerializer(many=True)
    class Meta:
        fields = '__all__'
        model = Test_this



   
class ResultSerializer(serializers.ModelSerializer):
    the_test = Test_thisSerializer#(null=True)
    class Meta:
        model = Result
        fields = ["the_test", "owner", "id", "score", "correct", "wrong", "percent", "total", "time", "created_at", "updated_at"]
       
    def create(self, validated_data):
        # the_tests_data = validated_data.pop('the_test')
        result = Result.objects.create(**validated_data)
        # for the_test_data in the_tests_data:
        #     Test_this.objects.create(result=result, **the_test_data)
        return result

class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Drink

class UserSerializer(serializers.ModelSerializer):
    # This model serializer will be used for User creation
    # The login serializer also inherits from this serializer
    # in order to require certain data for login
    class Meta:
        # get_user_model will get the user model (this is required)
        # https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#referencing-the-user-model
        model = get_user_model()
        fields = ('id', 'email', 'password')
        extra_kwargs = { 'password': { 'write_only': True, 'min_length': 5 } }

    # This create method will be used for model creation
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

class UserRegisterSerializer(serializers.Serializer):
    # Require email, password, and password_confirmation for sign up
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True)
    password_confirmation = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # Ensure password & password_confirmation exist
        if not data['password'] or not data['password_confirmation']:
            raise serializers.ValidationError('Please include a password and password confirmation.')

        # Ensure password & password_confirmation match
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError('Please make sure your passwords match.')
        # if all is well, return the data
        return data

class ChangePasswordSerializer(serializers.Serializer):
    model = get_user_model()
    old = serializers.CharField(required=True)
    new = serializers.CharField(required=True)
    password_confirmation = serializers.CharField(required=True, write_only=True)
    def validate(self, data):
        # Ensure password & password_confirmation exist
        if not data['new'] or not data['password_confirmation']:
            raise serializers.ValidationError('Please include a password and password confirmation.')

        # Ensure password & password_confirmation match
        if data['new'] != data['password_confirmation']:
            raise serializers.ValidationError('Please make sure your passwords match.')
        # if all is well, return the data
        return data
    
