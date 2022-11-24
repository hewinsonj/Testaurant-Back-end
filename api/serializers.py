from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models.mango import Mango
from .models.question import Question
from .models.question_new import Question_new
from .models.user import User
from .models.food import Food
from .models.drink import Drink
from .models.test import Test
from .models.quiz import Quiz
from .models.result import Result
from .models.quiz_test import Quiz_test
from .models.test_many import Test_many
from .models.test_test import Test_test
from .models.test_this import Test_this

class MangoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mango
        fields = ('id', 'name', 'color', 'ripe', 'owner')

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Question

class Question_newSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Question_new

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Food

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Test
        fields = ["__all__"]
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        test = Test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test=test, **question_data)
        return test

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Quiz
        fields = ["__all__"]
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(quiz=quiz, **question_data)
        return quiz
    
class Test_thisSerializer(serializers.ModelSerializer):
    question_news = Question_newSerializer(many=True)
    class Meta:
        model = Test_this
        fields = ["__all__"]
    def create(self, validated_data):
        question_news_data = validated_data.pop('question_news')
        test_this = Test_this.objects.create(**validated_data)
        for question_new_data in question_news_data:
            Question_new.objects.create(test_this=test_this, **question_new_data)
        return test_this

class ResultSerializer(serializers.ModelSerializer):
    the_tests = Test_thisSerializer(many=True)
    class Meta:
        model = Result
        fields = ["__all__"]
    def create(self, validated_data):
        the_test_data = validated_data.pop('tests')
        result = result.objects.create(**validated_data)
        for the_test_data in the_test_data:
            Test_this.objects.create(result=result, **the_test_data)
        return result

class Quiz_testSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Quiz_test
        fields = ["__all__"]
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz_test = Quiz_test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(quiz_test=quiz_test, **question_data)
        return quiz_test

class Test_manySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Test_many
        fields = ["__all__"]
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        test_many = Test_many.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test_many=test_many, **question_data)
        return test_many

class Test_testSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Test_test
        fields = ["__all__"]
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        test_test = Test_test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test_test=test_test, **question_data)
        return test_test

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
