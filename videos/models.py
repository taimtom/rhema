from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.db.models.signals import pre_save, post_save

from .utils import unique_slug_generator

from markdown_deux import markdown
from django.utils.safestring import mark_safe
# Create your models here.
User = settings.AUTH_USER_MODEL

# Create your models here.
class VideosdbQuerySet(models.query.QuerySet):
	def search(self,query):
		return self.filter(
			Q(title__icontains=query)|
			Q(description__icontains=query)|
			Q(writtenby__icontains=query)


			).distinct()

class VideosdbManager(models.Manager):
	def get_queryset(self):
		return VideosdbQuerySet(self.model, using=self._db)

	def search(self,query):
		return self.get_queryset().search(query)


class Videosdb(models.Model):
	title= models.CharField(max_length=50)
	writtenby=models.CharField(max_length=50)
	owner= models.ForeignKey(User, on_delete= models.CASCADE, default=1)
	videofile= models.FileField(upload_to='videos')
	image= models.ImageField(upload_to='videos/images')
	description=models.TextField(help_text='Seperate different lines or add paragraph by double comma (,,) ')
	public=models.BooleanField(default=False)
	timestamp=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now_add=True)
	slug   = models.SlugField(null=True, blank= True)

	objects=VideosdbManager()

	def __str__(self):
		return self.title

	def get_description(self):
		return self.description.split(',,') 

	def get_absolute_url(self):
		return reverse("video_detail", kwargs={'slug':self.slug})

	@property
	def get_content_type(self):
		instance=self
		content_type=ContentType.objects.get_for_model(instance.__class__)
		return content_type
	def get_markdown(self):
		description=self.description
		markdown_text=markdown(description)
		return mark_safe(markdown_text)
	class Meta:
		ordering=["-timestamp","-updated"]

def rl_pre_save_receiver(sender, instance, *args, **kwargs):
	instance.title = instance.title.capitalize()
	if not instance.slug:
		instance.slug =unique_slug_generator(instance)
pre_save.connect(rl_pre_save_receiver, sender=Videosdb)
