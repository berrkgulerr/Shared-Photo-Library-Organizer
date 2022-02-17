from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name='home'),

    path('view_collection/<str:pk>/', views.viewCollection, name='view_collection'),
    path('view_view/<str:pk>/', views.viewView, name='view_view'),
    path('view_photo/<str:pk>/', views.viewPhoto, name='view_photo'),
    path('view_photo_view/<str:pk>/', views.viewPhotoView, name='view_photo_view'),

    path('dashboard_views/<str:pk>/', views.dashboard_views, name='dashboard_views'),

    path('add_collection/', views.addCollection, name='add_collection'),
    path('add_photo/<str:pk>/', views.addPhoto, name='add_photo'),
    path('add_view/<str:pk>/', views.addView, name='add_view'),


    path('delete_collection/<str:pk>/', views.deleteCollection, name='delete_collection'),
    path('share_collection/<str:pk>/', views.shareCollection, name='share_collection'),
    path('unshare_collection/<str:pk>/', views.unshareCollection, name='unshare_collection'),

    path('delete_view/<str:pk>/', views.deleteView, name='delete_view'),
    path('update_view/<str:pk>/', views.updateView, name='update_view'),
    path('share_view/<str:pk>/', views.shareView, name='share_view'),
    path('unshare_view/<str:pk>/', views.unshareView, name='unshare_view'),

    path('update_photo/<str:pk>/', views.updatePhoto, name='update_photo'),
    path('delete_photo/<str:pk>/', views.deletePhoto, name='delete_photo'),

]
