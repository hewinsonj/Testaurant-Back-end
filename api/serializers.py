# from django.contrib.auth import get_user_model
# from rest_framework import serializers


# from .models.question_new import Question_new
# from .models.user import User
# from .models.food import Food
# from .models.drink import Drink
# from .models.result import Result
# from .models.test_this import Test_this

# class Question_newSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = '__all__'
#         model = Question_new

# class FoodSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = '__all__'
#         model = Food
    
# # class Test_thisSerializer(serializers.ModelSerializer):
# #     question_new = Question_newSerializer(many=True, read_only=True)
# #     class Meta:
# #         model = Test_this
# #         fields = ('name', 'question_new', 'owner', 'created_at', 'updated_at', 'id')
# #     def create(self, validated_data):
# #         # question_new_data = validated_data.pop('question_new')
# #         test_this = Test_this.objects.create(**validated_data)
# #         # for question_new_data in question_new_data:
# #         #     Question_new.objects.create(test_this=test_this, **question_new_data)
# #         return test_this

# class Test_thisSerializer(serializers.ModelSerializer):
#     # Allow the frontend to send a list of `question_new` IDs
#     question_new = serializers.PrimaryKeyRelatedField(
#         queryset=Question_new.objects.all(),
#         many=True
#     )

#     class Meta:
#         model = Test_this
#         fields = ('name', 'question_new', 'owner', 'created_at', 'updated_at', 'id')

#     def create(self, validated_data):
#         # Extract `question_new` data (list of IDs)
#         question_new_data = validated_data.pop('question_new', [])
        
#         # Create the `Test_this` object
#         test_this = Test_this.objects.create(**validated_data)
        
#         # Assign the many-to-many relationship
#         test_this.question_new.set(question_new_data)
        
#         return test_this

# class Test_thisReadSerializer(serializers.ModelSerializer):
#     question_new = serializers.StringRelatedField(many=True)
#     class Meta:
#         fields = '__all__'
#         model = Test_this

# class Test_thisGetSerializer(serializers.ModelSerializer):
#     question_new = Question_newSerializer(many=True)
#     class Meta:
#         fields = '__all__'
#         model = Test_this



   
# # class ResultSerializer(serializers.ModelSerializer):
#     # the_test = Test_thisSerializer()#(null=True)
#     # class Meta:
#     #     model = Result
#     #     fields = ["the_test", "owner", "id", "score", "correct", "wrong", "percent", "total", "time", "created_at", "updated_at"]
       
#     # def create(self, validated_data):
#     #     # the_tests_data = validated_data.pop('the_test')
#     #     result = Result.objects.create(**validated_data)
#     #     # for the_test_data in the_tests_data:
#     #     #     Test_this.objects.create(result=result, **the_test_data)
#     #     return result
# class ResultSerializer(serializers.ModelSerializer):
#     the_test = serializers.PrimaryKeyRelatedField(queryset=Test_this.objects.all())

#     class Meta:
#         model = Result
#         fields = [
#             "the_test", "owner", "id", "score", "correct", "wrong",
#             "percent", "total", "time", "created_at", "updated_at"
#         ]

#     def create(self, validated_data):
#         return Result.objects.create(**validated_data)


# class DrinkSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = '__all__'
#         model = Drink

# # class UserSerializer(serializers.ModelSerializer):
# #     # This model serializer will be used for User creation
# #     # The login serializer also inherits from this serializer
# #     # in order to require certain data for login
# #     class Meta:
# #         # get_user_model will get the user model (this is required)
# #         # https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#referencing-the-user-model
# #         model = get_user_model()
# #         fields = ('id', 'email', 'password')
# #         extra_kwargs = { 'password': { 'write_only': True, 'min_length': 5 } }

# #     # This create method will be used for model creation
# #     def create(self, validated_data):
# #         return get_user_model().objects.create_user(**validated_data)

# # class UserSerializer(serializers.ModelSerializer):
# #     assigned_tests = serializers.PrimaryKeyRelatedField(
# #         many=True,
# #         queryset=Test_this.objects.all(),
# #         required=False
# #     )

# #     class Meta:
# #         model = get_user_model()
# #         fields = (
# #             'id', 'email', 'password',
# #             'first_name', 'last_name',
# #             'role', 'hire_date',
# #             'assigned_tests',
# #         )
# #         extra_kwargs = {
# #             'password': {'write_only': True, 'min_length': 5}
# #         }

# #     def create(self, validated_data):
# #         return get_user_model().objects.create_user(**validated_data)

# class UserSerializer(serializers.ModelSerializer):
#     assigned_tests = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=Test_this.objects.all(),
#         required=False
#     )

#     class Meta:
#         model = get_user_model()
#         fields = (
#             'id', 'email', 'password',
#             'first_name', 'last_name',
#             'role', 'hire_date', 'is_superuser', 'is_active', 'is_staff',
#             'assigned_tests',
#         )
#         extra_kwargs = {
#             'password': {'write_only': True, 'min_length': 5}
#         }

#     def create(self, validated_data):
#         return get_user_model().objects.create_user(**validated_data)

# # class UserRegisterSerializer(serializers.Serializer):
# #     # Require email, password, and password_confirmation for sign up
# #     email = serializers.CharField(max_length=300, required=True)
# #     password = serializers.CharField(required=True)
# #     password_confirmation = serializers.CharField(required=True, write_only=True)

# #     def validate(self, data):
# #         # Ensure password & password_confirmation exist
# #         if not data['password'] or not data['password_confirmation']:
# #             raise serializers.ValidationError('Please include a password and password confirmation.')

# #         # Ensure password & password_confirmation match
# #         if data['password'] != data['password_confirmation']:
# #             raise serializers.ValidationError('Please make sure your passwords match.')
# #         # if all is well, return the data
# #         return data

# class UserRegisterSerializer(serializers.Serializer):
#     email = serializers.CharField(max_length=300, required=True)
#     password = serializers.CharField(required=True, write_only=True, min_length=5)
#     password_confirmation = serializers.CharField(required=True, write_only=True)
#     first_name = serializers.CharField(required=False, allow_blank=True)
#     last_name = serializers.CharField(required=False, allow_blank=True)
#     role = serializers.CharField(required=False, allow_blank=True)
#     hire_date = serializers.DateField(required=False, allow_null=True)
#     is_superuser = serializers.BooleanField(default=False)
#     is_active = serializers.BooleanField(default=True)
#     is_staff = serializers.BooleanField(default=False)

#     def validate(self, data):
#         if data['password'] != data['password_confirmation']:
#             raise serializers.ValidationError("Passwords must match.")
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password_confirmation')
#         return User.objects.create_user(**validated_data)
    

# class ChangePasswordSerializer(serializers.Serializer):
#     model = get_user_model()
#     old = serializers.CharField(required=True)
#     new = serializers.CharField(required=True)
#     password_confirmation = serializers.CharField(required=True, write_only=True)
#     def validate(self, data):
#         # Ensure password & password_confirmation exist
#         if not data['new'] or not data['password_confirmation']:
#             raise serializers.ValidationError('Please include a password and password confirmation.')

#         # Ensure password & password_confirmation match
#         if data['new'] != data['password_confirmation']:
#             raise serializers.ValidationError('Please make sure your passwords match.')
#         # if all is well, return the data
#         return data
    


from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models.question_new import Question_new
from .models.user import User
from .models.food import Food
from .models.drink import Drink
from .models.result import Result
from .models.test_this import Test_this


### Question Serializer ###
class Question_newSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question_new
        fields = '__all__'


### Food Serializer ###
class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'
        read_only_fields = ['owner']


### Drink Serializer ###
class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'
        read_only_fields = ['owner']


### Test Serializers ###
class Test_thisSerializer(serializers.ModelSerializer):
    question_new = serializers.PrimaryKeyRelatedField(
        queryset=Question_new.objects.all(),
        many=True
    )

    class Meta:
        model = Test_this
        fields = ('id', 'name', 'question_new', 'owner', 'created_at', 'updated_at')

    def create(self, validated_data):
        questions = validated_data.pop('question_new', [])
        test = Test_this.objects.create(**validated_data)
        test.question_new.set(questions)
        return test


class Test_thisReadSerializer(serializers.ModelSerializer):
    question_new = serializers.StringRelatedField(many=True)

    class Meta:
        model = Test_this
        fields = '__all__'


class Test_thisGetSerializer(serializers.ModelSerializer):
    question_new = Question_newSerializer(many=True)

    class Meta:
        model = Test_this
        fields = '__all__'


### Result Serializer ###
class ResultSerializer(serializers.ModelSerializer):
    the_test = serializers.PrimaryKeyRelatedField(queryset=Test_this.objects.all())

    class Meta:
        model = Result
        fields = [
            'id', 'the_test', 'owner', 'score', 'correct', 'wrong',
            'percent', 'total', 'time', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        the_test = validated_data.get('the_test')
        owner = validated_data.get('owner')

        result = Result.objects.create(**validated_data)

        if owner and the_test in owner.assigned_tests.all():
            owner.assigned_tests.remove(the_test)
            owner.save()

        return result


### User Serializer ###
class UserSerializer(serializers.ModelSerializer):
    assigned_tests = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Test_this.objects.all(),
        required=False
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'role', 'hire_date',
            'is_superuser', 'is_active', 'is_staff',
            'assigned_tests', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


### User Registration Serializer ###
class UserRegisterSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=5)
    password_confirmation = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)
    hire_date = serializers.DateField(required=False, allow_null=True)
    is_superuser = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        return get_user_model().objects.create_user(**validated_data)


### Password Change Serializer ###
class ChangePasswordSerializer(serializers.Serializer):
    old = serializers.CharField(required=True)
    new = serializers.CharField(required=True)
    password_confirmation = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if not data['new'] or not data['password_confirmation']:
            raise serializers.ValidationError('Please include a new password and confirmation.')
        if data['new'] != data['password_confirmation']:
            raise serializers.ValidationError('New passwords do not match.')
        return data