from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),          
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'), 
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_post, name='upload_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('toggle-like/<int:post_id>/', views.toggle_like, name='toggle_like'),
       
]

