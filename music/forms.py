from django import forms
from .models import Musicdb
from pagedown.widgets import PagedownWidget

class MusicCreateForm(forms.ModelForm):
	musicfile=forms.FileField(label='Upload Music')
	image=forms.ImageField(label='Music Image')	
	description=forms.CharField(label='Lyrics and artist or song description', widget=PagedownWidget)

	class Meta:
		model =Musicdb
		fields =[
		"title",
		"artist",
		"musicfile",
		"image",
		"description"
		
		
		]
