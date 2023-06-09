from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
    path('', views.index),
    path('users/', views.users),
    path('notes/<str:id>/', views.notes),
    path('notes/', views.notes),
    path('post_note/', views.post_note),
    path('delete/<str:id>/', views.post_delete),
    path('stocks/', views.stock_info),
    path('login/', views.login_user),
    path('signup/', views.signup),
    path('predict/', views.stock_predict),
]