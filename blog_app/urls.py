from django.urls import path,include
from .views import *
from . import views

urlpatterns = [
    path('index/', views.index_view.as_view(), name='index'),
    path('home_page/<userid>', views.HomePageView.as_view(), name='home_page'),
    path('home_page/mypage/<userid>', views.MyPageView.as_view(), name='my_page'),
    path('create_article/<userid>', views.ArticleCreateView.as_view(), name='create_article'),
    path('create_user/', views.UserCreateView.as_view(), name='create_user'),
    path('login/', views.MyLoginView.as_view(), name="login"),
    path('logout/', views.MyLogoutView.as_view(), name="logout"),
    path('follow/<pk>', views.FollowView.as_view(), name="follow"),
    path('unfollow/<pk>', views.UnfollowView, name="unfollow"),
]