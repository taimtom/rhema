from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
# Create your views here.
from .models import Videosdb
from .forms import VideoCreateForm

from urllib.parse import quote

from django.core.paginator import Paginator


from comments.forms import CommentForm
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404,redirect



class VideoListView(LoginRequiredMixin,ListView):
	def get_queryset(self):
		
		query=self.request.GET.get('search')
		qs=Videosdb.objects.order_by('-timestamp')
		
		
		return qs	
	def get_context_data(self,*args, **kwargs):
		context=super(VideoListView,self).get_context_data(*args,**kwargs)
		qs=Videosdb.objects.order_by('-timestamp')
		paginator=Paginator(qs,15)
		page=self.request.GET.get('page')
		object_listing=paginator.get_page('page')
		context['object_list']=object_listing
		context['counted']=qs.count()
		query=self.request.GET.get('search')
		if query:
			query=query.strip()
			qs = qs.search(query)
		return context
		

def VideoDetailView(request, slug=None):
	
	
	instance = get_object_or_404(Videosdb, slug=slug)
	share_string= quote(instance.description)
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
	return render(request,'videos/videosdb_detail.html',context)
@login_required
def videocreateview(request):
	form = VideoCreateForm(request.POST, request.FILES)
	if form.is_valid():
		instance=form.save(commit=False)
		instance.owner=request.user
		instance.save()
		#messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context={
	"form":form
	}
	return render(request, "videos/form.html", context)
