from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.login_page, name="login"),
    path('user/', views.user_page),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.SignUp, name='signup'),
    path('createuser/', views.createuser),
    path('createpost/', views.create_redirect, name='create'),
    path('pushpost/', views.create_post),
    path('check/', views.check, name='check'),
    path('check_post/', views.post_check),
    path('delete/<str:date>', views.post_delete),
]