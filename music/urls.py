from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from .views import (
	MusicListView,
	MusicDetailView,
    musiccreateview,
    MusicArtist
	)
urlpatterns = [
    path('',MusicListView.as_view(), name='music_list'),
    path('<slug>/',MusicDetailView, name='music_detail'),
    path('post/create/',musiccreateview, name='music_create'),
    url(r'^(?P<artist>[\w-]+)/$', MusicArtist.as_view(), name='artist_detail'),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
