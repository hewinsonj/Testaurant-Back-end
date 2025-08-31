from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models.question_new import Question_new
from .models.user import User
from .models.food import Food
from .models.drink import Drink
from .models.result import Result
from .models.test_this import Test_this
from .models.restaurant import Restaurant
from .models.editLog import EditLog


### Restaurant Serializer ###
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
        # Owner is set from the request in the view; timestamps are auto
        read_only_fields = ['owner', 'created_at', 'updated_at']



### EditLog Serializer (optional API exposure) ###
class EditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditLog
        fields = '__all__'
        read_only_fields = ['edit_date']

### Question Serializer ###
class Question_newSerializer(serializers.ModelSerializer):
    # Accept restaurant as a FK id or null; don't force clients to send nested objects
    restaurant = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(), required=False, allow_null=True
    )
    # Let the view set owner (e.g., save(owner=request.user)); don't require it from client
    owner = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=False
    )

    class Meta:
        model = Question_new
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


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
        fields = ('id', 'name', 'question_new', 'owner', 'created_at', 'updated_at', 'restaurant', 'allotted_time')

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
            'id',
            'score',
            'correct',
            'wrong',
            'wrong_question_ids',
            'total',
            'percent',
            'time',
            'time_completed',
            'the_test',
            'owner',
            'restaurant',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

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
            'assigned_tests', 'password', 'restaurant'
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