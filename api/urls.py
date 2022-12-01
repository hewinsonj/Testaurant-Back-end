from django.urls import path
from .views.mango_views import Mangos, MangoDetail
from .views.food_views import Foods, FoodDetail
from .views.question_views import Questions, QuestionDetail
from .views.question_new_views import Question_news, Question_newDetail
from .views.test_views import Tests, TestDetail
from .views.quiz_views import Quizs, QuizDetail
from .views.quiz_test_views import Quiz_tests, Quiz_testDetail
from .views.test_many_views import Test_manys, Test_manyDetail
from .views.test_test_views import Test_tests, Test_testDetail
from .views.test_this_views import Test_thiss, Test_thisDetail
from .views.result_views import Results, ResultDetail
from .views.drink_views import Drinks, DrinkDetail
from .views.user_views import SignUp, SignIn, SignOut, ChangePassword, Users


urlpatterns = [
  	# Restful routing
    path('mangos/', Mangos.as_view(), name='mangos'),
    path('mangos/<int:pk>/', MangoDetail.as_view(), name='mango_detail'),
    path('results/', Results.as_view(), name='results'),
    path('results/<int:pk>/', ResultDetail.as_view(), name='result_detail'),
    path('quizs/', Quizs.as_view(), name='quizs'),
    path('quizs/<int:pk>/', QuizDetail.as_view(), name='quiz_detail'),
    path('quiz_tests/', Quiz_tests.as_view(), name='quizs'),
    path('quiz_tests/<int:pk>/', Quiz_testDetail.as_view(), name='quiz_detail'),
    path('test_manys/', Test_manys.as_view(), name='test_manys'),
    path('test_manys/<int:pk>/', Test_manyDetail.as_view(), name='test_many'),
    path('test_tests/', Test_tests.as_view(), name='test_tests'),
    path('test_tests/<int:pk>/', Test_testDetail.as_view(), name='test_test'),
    path('test_thiss/', Test_thiss.as_view(), name='test_thiss'),
    path('test_thiss/<int:pk>/', Test_thisDetail.as_view(), name='test_this'),
    path('tests/', Tests.as_view(), name='tests'),
    path('tests/<int:pk>/', TestDetail.as_view(), name='test_detail'),
    path('drinks/', Drinks.as_view(), name='drinks'),
    path('drinks/<int:pk>/', DrinkDetail.as_view(), name='drink_detail'),
    path('foods/', Foods.as_view(), name='foods'),
    path('foods/<int:pk>/', FoodDetail.as_view(), name='food_detail'),
    path('questions/', Questions.as_view(), name='mangos'),
    path('questions/<int:pk>/', QuestionDetail.as_view(), name='mango_detail'),
    path('question_news/', Question_news.as_view(), name='question_new'),
    path('question_news/<int:pk>/', Question_newDetail.as_view(), name='question_new_detail'),
    path('sign-up/', SignUp.as_view(), name='sign-up'),
    path('sign-in/', SignIn.as_view(), name='sign-in'),
    path('sign-out/', SignOut.as_view(), name='sign-out'),
    path('change-pw/', ChangePassword.as_view(), name='change-pw'),
    path('employees/', Users.as_view(), name='users')
]
