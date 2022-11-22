from django.urls import path
from .views.mango_views import Mangos, MangoDetail
from .views.food_views import Foods, FoodDetail
from .views.question_views import Questions, QuestionDetail
from .views.test_views import Tests, TestDetail
from .views.drink_views import Drinks, DrinkDetail
from .views.user_views import SignUp, SignIn, SignOut, ChangePassword


urlpatterns = [
  	# Restful routing
    path('mangos/', Mangos.as_view(), name='mangos'),
    path('mangos/<int:pk>/', MangoDetail.as_view(), name='mango_detail'),
    path('tests/', Tests.as_view(), name='tests'),
    path('tests/<int:pk>/', TestDetail.as_view(), name='test_detail'),
    path('drinks/', Drinks.as_view(), name='drinks'),
    path('drinks/<int:pk>/', DrinkDetail.as_view(), name='drink_detail'),
    path('foods/', Foods.as_view(), name='foods'),
    path('foods/<int:pk>/', FoodDetail.as_view(), name='food_detail'),
    path('questions/', Questions.as_view(), name='mangos'),
    path('questions/<int:pk>/', QuestionDetail.as_view(), name='mango_detail'),
    path('sign-up/', SignUp.as_view(), name='sign-up'),
    path('sign-in/', SignIn.as_view(), name='sign-in'),
    path('sign-out/', SignOut.as_view(), name='sign-out'),
    path('change-pw/', ChangePassword.as_view(), name='change-pw')
]
