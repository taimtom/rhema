from itertools import chain

from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from urllib.parse import quote

from django.urls import reverse

from django.db.models import Q
from django.http import HttpResponseRedirect,Http404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import View, ListView, DetailView
from django.utils import timezone

# Create your views here.

from comments.forms import CommentForm
from comments.models import Comment
from music.models import Musicdb
from videos.models import Videosdb
from .models import Rhemadb
from .forms import RhemadbCreateForm

@login_required
def rhemacreateview(request):
	form = RhemadbCreateForm(request.POST, request.FILES)
	if form.is_valid():
		instance=form.save(commit=False)
		instance.owner=request.user
		instance.save()
		messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context={
	"form":form
	}
	return render(request, "rhema/form.html", context)


class HomeView(LoginRequiredMixin,View):
	def get(self,request,*args,**kwargs):
		print(self.request.user)
		
		page_owner=self.request.user
		user=request.user
		is_following_user_ids=[x.user.id for x in user.is_following.all()]
		music_query=Musicdb.objects.filter(Q(owner__id__in=is_following_user_ids)|Q( owner=user)).order_by("-timestamp")
		video_query=Videosdb.objects.filter(Q(owner__id__in=is_following_user_ids)|Q( owner=user)).order_by("-timestamp")
		myword=Rhemadb.objects.filter((Q(owner__id__in=is_following_user_ids)|Q( owner=user))& Q( public=True)).order_by("-timestamp")

		queryset_chain=chain(
						myword,
						music_query,
						video_query
					)
		qs=sorted(queryset_chain,
					key=lambda instance:instance.timestamp,
					reverse=True)
		self.count=len(qs)
		counted=self.count
		paginator=Paginator(qs,20)
		page=request.GET.get('page')
		object_list=paginator.get_page(page)
		

		context={
			'object_list':object_list,
			'counted':self.count,
		}
		return render(request,'rhema/home-feed.html',context)

class RhemaListView(LoginRequiredMixin,ListView):
	#queryset=Rhemadb.objects.order_by('-timestamp')
	
	def get_queryset(self):
		
		query=self.request.GET.get('search')
		qs=Rhemadb.objects.order_by('-timestamp')
		if query:
			query=query.strip()
			qs = qs.search(query)
		
		return qs

@login_required
def RhemaDetailView(request, slug=None):
	
	
	instance = get_object_or_404(Rhemadb, slug=slug)
	share_string= quote(instance.bodytext)
	initial_data={
		
		"content_type":instance.get_content_type,
		"object_id":instance.id
	}
	form=CommentForm(request.POST or None, initial=initial_data)
	if form.is_valid():
		c_type=form.cleaned_data.get("content_type")
		content_type=ContentType.objects.get(model=c_type)
		obj_id=form.cleaned_data.get("object_id")
		content_data=form.cleaned_data.get("content")
		parent_obj=None
		try:
			parent_id=int(request.POST.get('parent_id'))
		except:
			parent_id=None
		if parent_id:
			parent_qs=Comment.objects.filter(id=parent_id)
			if parent_qs.exists():
				parent_obj=parent_qs.first()
				print(parent_obj)
		new_comment, created=Comment.objects.get_or_create(

			user=request.user,
			content_type=content_type,
			object_id=obj_id,
			content=content_data,
			parent=parent_obj
			)
		return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

	comments=Comment.objects.filter_by_instance(instance)
	
	context={
		'share_string':share_string,
		'instance':instance,
		'comments':comments,
		'comment_form':form
	}
	return render(request,'rhema/rhema_detail.html',context)


