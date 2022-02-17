from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name='home'),

    path('view_collection/<str:pk>/', views.viewCollection, name='view_collection'),
    path('view_view/<str:pk>/', views.viewView, name='view_view'),

    path('add_collection/', views.addCollection, name='add_collection'),
    path('add_photo/', views.addPhoto, name='add_photo'),
    path('add_view/', views.addView, name='add_view'),


    path('delete_collection/', views.deleteCollection, name='delete_collection'),
    path('share_collection/', views.shareCollection, name='share_collection'),
    path('unshare_collection/', views.unshareCollection, name='unshare_collection'),

    path('delete_view/', views.deleteView, name='delete_view'),
    path('update_view/', views.updateView, name='update_view'),
    path('share_view/', views.shareView, name='share_view'),
    path('unshare_view/', views.unshareView, name='unshare_view'),

    path('update_photo/', views.updatePhoto, name='update_photo'),
    path('delete_photo/', views.deletePhoto, name='delete_photo'),

]
