from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from .views import (
	VideoListView,
	VideoDetailView,
    videocreateview,
	)
urlpatterns = [
    path('',VideoListView.as_view(), name='video_list'),
    path('<slug>/',VideoDetailView, name='video_detail'),
    path('post/create/',videocreateview, name='video_create'),
   
] 
