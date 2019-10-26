from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
# Create your views here.
from .models import Musicdb
from .forms import MusicCreateForm

from django.core.paginator import Paginator

from urllib.parse import quote

from comments.forms import CommentForm
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404,redirect




class MusicListView(LoginRequiredMixin,ListView):
	def get_queryset(self):
		
		query=self.request.GET.get('search')
		qs=Musicdb.objects.order_by('-timestamp')
		if query:
			query=query.strip()
			qs = qs.search(query)
		
		return qs	
	def get_context_data(self,*args, **kwargs):
		context=super(MusicListView,self).get_context_data(*args,**kwargs)
		qs=Musicdb.objects.order_by('-timestamp')
		paginator=Paginator(qs,15)
		page=self.request.GET.get('page')
		object_listing=paginator.get_page('page')
		context['object_list']=object_listing
		context['counted']=qs.count()
		
		
		return context

			
def MusicDetailView(request, slug=None):
	
	
	instance = get_object_or_404(Musicdb, slug=slug)
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
	return render(request,'music/musicdb_detail.html',context)

@login_required
def musiccreateview(request):
	form = MusicCreateForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance=form.save(commit=False)
		instance.owner=request.user
		instance.save()
		#messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context={
	"form":form
	}
	return render(request, "music/form.html", context)


class MusicArtist(LoginRequiredMixin,DetailView):
	template_name='music/music_artist.html'

	def get_object(self):
		artist=self.kwargs.get("artist")
		if artist is None:
			raise Http404
		return get_object_or_404(Musicdb,artist__iexact=artist)
