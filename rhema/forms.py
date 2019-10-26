from django import forms
from .models import Rhemadb

from pagedown.widgets import PagedownWidget

class RhemadbCreateForm(forms.ModelForm):
	bodytext=forms.CharField(widget=PagedownWidget)
	class Meta:
		model =Rhemadb
		fields =[
		"headline",
		"public",
		"image",
		"file",
		"bodytext",
		
		]






