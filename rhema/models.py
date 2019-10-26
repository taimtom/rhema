from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

from .utils import unique_slug_generator

from markdown_deux import markdown

from django.utils.safestring import mark_safe
# Create your models here.
User = settings.AUTH_USER_MODEL

class RhemadbQuerySet(models.QuerySet):
	def search(self,query=None):
		qs=self
		if query is not None:
			look_up=(Q(headline__icontains=query)|
					Q(bodytext__icontains=query))

			qs=qs.filter(look_up).distinct()
		return qs

class RhemadbManager(models.Manager):
	def get_queryset(self):
		return RhemadbQuerySet(self.model, using=self._db)

	def search(self,query=None):
		return self.get_queryset().search(query)

class Rhemadb(models.Model):
	owner= models.ForeignKey(User, on_delete= models.CASCADE)
	headline=models.CharField(max_length=30)
	image=models.ImageField(upload_to='rhema/images',blank=True, null=True, verbose_name='image')
	file=models.FileField(upload_to='videos', null=True,blank=True)
	bodytext=models.TextField(help_text='Seperate different lines or add paragraph by double comma (,,) ')
	public=models.BooleanField(default=False)
	timestamp=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now_add=True)
	slug   = models.SlugField(null=True, blank= True)

	objects=RhemadbManager()

	def __str__(self):
		return self.headline

	def get_absolute_url(self):
		return reverse("rhema_detail", kwargs={'slug':self.slug})
	def get_bodytext(self):
		return self.bodytext.split(',,') 

	def get_markdown(self):
		bodytext=self.bodytext
		markdown_text=markdown(bodytext)
		return mark_safe(markdown_text)
	@property
	def get_content_type(self):
		instance=self
		content_type=ContentType.objects.get_for_model(instance.__class__)
		return content_type

	class Meta:
		ordering=["-timestamp","-updated"]



def rl_pre_save_receiver(sender, instance, *args, **kwargs):
	instance.headline = instance.headline.capitalize()
	if not instance.slug:
		instance.slug =unique_slug_generator(instance)
pre_save.connect(rl_pre_save_receiver, sender=Rhemadb)

