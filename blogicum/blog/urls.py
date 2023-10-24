from blog import views
from django.urls import path

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment,
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>',
         views.delete_comment,
         name='delete_comment'),
    path('profile/<str:name>/', views.info_profile, name='profile'),
    path('edit_profile/<slug:name>',
         views.edit_profile,
         name='edit_profile'),
]
