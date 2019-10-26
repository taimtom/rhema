from django .conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.urls import reverse
from .utils import code_generator
from django.contrib.auth import get_user_model

from django.db.models import Q
User=get_user_model()



class MyProfileManager(models.Manager):
	def toggle_follow(self,request_user, username_to_toggle):
		myprofile_=MyProfile.objects.get(user__username__iexact=username_to_toggle)
		user=request_user
		is_following=False
		if user in myprofile_.followers.all():
			myprofile_.followers.remove(user)
		else:
			myprofile_.followers.add(user)
			is_following=True
		return myprofile_,is_following




class MyProfile(models.Model):
	user 		= models.OneToOneField(User, on_delete=models.CASCADE)
	followers	= models.ManyToManyField(User, related_name='is_following', blank=True)
	#following	= models.ManyToManyField(User, related_name='following',blank=True)
	activation_key= models.CharField(max_length=120,blank=True, null=True)
	activated	= models.BooleanField(default=False)
	timestamp	= models.DateTimeField(auto_now_add=True)
	updated		= models.DateTimeField(auto_now_add=True)

	objects=MyProfileManager()
	def get_absolute_url(self):
		return reverse("detail", kwargs={'username':self.username})

	


	def __str__(self):
		return self.user.username

	def send_activation_email(self):
		print("activation")
		if not self.activated:

			self.activation_key=code_generator()
			self.save()
			path_ = reverse('activate', kwargs={"code":self.activation_key})
			subject='Activation Key'
			from_email=settings.DEFAULT_FROM_EMAIL
			message=f'Activate your account here : {path_}'
			recipient_list=[self.user.email]
			html_message=f'<p>Activate your account here : {path_}</p>'
			sent_mail=False
			#sent_mail=send_mail(
			#	subject,
			#	message,
			#	from_email,
			#	recipient_list,
			#	fail_silently=False,
			#	html_message=html_message)
			print(html_message)
			return sent_mail
		

def post_save_user_receiver(sender,instance,created,*args, **kwargs):


	if created:
		myprofile, is_created  = MyProfile.objects.get_or_create(user=instance)
		default_user_profile = MyProfile.objects.get_or_create(user__id=1)[0]
		default_user_profile.followers.add(instance)
		myprofile.followers.add(default_user_profile.user)
		myprofile.followers.add(1)


post_save.connect(post_save_user_receiver, sender=User)



