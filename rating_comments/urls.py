from django.urls import path
from . import views

app_name = 'rating_comments'

urlpatterns = [
    path('reply/<slug:slug>/<int:comment_id>/', views.PostAddReplyView.as_view(), name='add_reply'),
    path('comment/delete/<slug:slug>/<int:comment_id>/', views.PostDeleteCommentView.as_view(), name='delete_comment'),
    path('rating/<slug:slug>/', views.PostAddRatingView.as_view(), name='add_rating')
]
