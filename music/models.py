from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.db.models.signals import pre_save, post_save

from markdown_deux import markdown

from django.utils.safestring import mark_safe

from .utils import unique_slug_generator

# Create your models here.
User = settings.AUTH_USER_MODEL


class MusicdbQuerySet(models.query.QuerySet):
	def search(self,query):
		return self.filter(
			Q(title__icontains=query)|
			Q(description__icontains=query)|
			Q(artist__icontains=query)

			).distinct()

class MusicdbManager(models.Manager):
	def get_queryset(self):
		return MusicdbQuerySet(self.model, using=self._db)

	def search(self,query):
		return self.get_queryset().search(query)

# Create your models here.
class Musicdb(models.Model):
	title= models.CharField(max_length=50)
	artist=models.CharField(max_length=50)
	owner= models.ForeignKey(User, on_delete= models.CASCADE)
	image= models.FileField(upload_to='music/images', null=True, verbose_name="")
	musicfile= models.FileField(upload_to='music', null=True, verbose_name="")
	public=models.BooleanField(default=False)
	description=models.TextField(help_text='Seperate different lines or add paragraph by double comma (,,) ')
	timestamp=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now_add=True)
	slug   = models.SlugField(null=True, blank= True)

	objects=MusicdbManager()

	def __str__(self):
		return self.title
	def get_absolute_url(self):
		return reverse("music_detail", kwargs={'slug':self.slug})

	def get_description(self):
		return self.description.split(',,') 

	def get_artist_url(self):
		return reverse("artist_detail", kwargs={'artist':self.slug})


	def get_markdown(self):
		description=self.description
		markdown_text=markdown(description)
		return mark_safe(markdown_text)
	@property
	def get_content_type(self):
		instance=self
		content_type=ContentType.objects.get_for_model(instance.__class__)
		return content_type

	class Meta:
		ordering=["-timestamp","-updated"]

def rl_pre_save_receiver(sender, instance, *args, **kwargs):
	instance.title = instance.title.capitalize()
	if not instance.slug:
		instance.slug =unique_slug_generator(instance)
pre_save.connect(rl_pre_save_receiver, sender=Musicdb)


