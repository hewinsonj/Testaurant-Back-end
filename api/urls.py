from django.urls import path
from .views.food_views import Foods, FoodDetail
from .views.question_new_views import Question_news, Question_newDetail
from .views.test_this_views import Test_thiss, Test_thisDetail
from .views.result_views import Results, ResultDetail, MyResults
from .views.drink_views import Drinks, DrinkDetail
from .views.user_views import SignUp, SignIn, SignOut, ChangePassword, Users,UserDetail


urlpatterns = [
  	# Restful routing
    path('results/', Results.as_view(), name='results'),
    path('results/<int:pk>/', ResultDetail.as_view(), name='result_detail'),
    path('test_thiss/', Test_thiss.as_view(), name='test_thiss'),
    path('test_thiss/<int:pk>/', Test_thisDetail.as_view(), name='test_this'),
    path('drinks/', Drinks.as_view(), name='drinks'),
    path('drinks/<int:pk>/', DrinkDetail.as_view(), name='drink_detail'),
    path('foods/', Foods.as_view(), name='foods'),
    path('foods/<int:pk>/', FoodDetail.as_view(), name='food_detail'),
    path('question_news/', Question_news.as_view(), name='question_new'),
    path('question_news/<int:pk>/', Question_newDetail.as_view(), name='question_new_detail'),
    path('sign-up/', SignUp.as_view(), name='sign-up'),
    path('sign-in/', SignIn.as_view(), name='sign-in'),
    path('sign-out/', SignOut.as_view(), name='sign-out'),
    path('change-pw/', ChangePassword.as_view(), name='change-pw'),
    path('employees/', Users.as_view(), name='users'),
    path('users/<int:pk>/', UserDetail.as_view(), name='users-detail'),
    path('results/', Results.as_view(), name='results'),
    path('results/mine/', MyResults.as_view(), name='my-results'),
]
