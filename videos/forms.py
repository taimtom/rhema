from django import forms
from .models import Videosdb

from pagedown.widgets import PagedownWidget

class VideoCreateForm(forms.ModelForm):
	description=forms.CharField(widget=PagedownWidget)
	class Meta:
		model =Videosdb
		fields =[
		"title",
		"writtenby",
		'image',
		"videofile",
		'description'
		
		
		]

