from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_post/', views.add_post, name='add_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('api/posts/', views.PostListCreateApiView.as_view(), name='post_list_create'),
    path('api/posts/delete', views.PostDeleteApiView.as_view(), name='post-delete'),
]