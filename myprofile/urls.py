from django.conf.urls import url

from .views import ProfileDetailView#,ProfileUpdate

app_name="myprofile"

urlpatterns=[
	url(r'^(?P<username>[\w-]+)/$', ProfileDetailView.as_view(), name='detail'),
	#url(r'^(?P<username>[\w-]+)/profile_edit/$', ProfileUpdate.as_view(), name='profile_edit'),
]