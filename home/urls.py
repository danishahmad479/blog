from django.urls import path 
from .views import *

urlpatterns = [
    path("register/", register ,name="register"),
    path("user_login/", user_login ,name="user_login"),
    path('', blog_list, name='blog_list'),
    path('post/<int:pk>/', blog_detail, name='blog_detail'),
    path('send-blog-email/', send_blog_email, name='send_blog_email'),
    path('post/<int:pk>/comment/', add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/',like_comment, name='like_comment'),
]