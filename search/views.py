
from itertools import chain

from django.core.paginator import Paginator

from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q
from django.http import HttpResponseRedirect,Http404
from django.views.generic import View, ListView, DetailView


#search models
from comments.models import Comment
from music.models import Musicdb
from videos.models import Videosdb
from rhema.models import Rhemadb
#from myprofile.models import MyProfile

# Create your views here.

class SearchView(LoginRequiredMixin,ListView):
	template_name='search/view.html'
	paginated_by=20
	count=0
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['count']=self.count
		context['query']=self.request.GET.get('search')
		return context
	def get_queryset(self):	
		request=self.request
		user=self.request.user
		is_following_user_ids=[x.user.id for x in user.is_following.all()]
		comment_query=Comment.objects.all().order_by("-timestamp")
		#profile_query=MyProfile.objects.all()
		music_query=Musicdb.objects.filter(Q(owner__id__in=is_following_user_ids)|Q( owner=user)).order_by("-timestamp")
		video_query=Videosdb.objects.filter(Q(owner__id__in=is_following_user_ids)|Q( owner=user)).order_by("-timestamp")
		myword=Rhemadb.objects.filter((Q(owner__id__in=is_following_user_ids)|Q( owner=user))& Q( public=True)).order_by("-timestamp")

		query=request.GET.get('search',None)
		if query is not None:
			query=query.strip()
			myword=myword.search(query)
			comment_query=comment_query.search(query)
			#profile_query=profile_query.search(query)
			music_query=music_query.search(query)
			video_query=video_query.search(query)

			queryset_chain=chain(
							myword,
							comment_query,
							#profile_query,
							music_query,
							video_query
						)
			qs=sorted(queryset_chain,
						key=lambda instance:instance.pk,
						reverse=True)
			self.count=len(qs)
			#paginator=Paginator(qs,5)
			#page=request.GET.get('page')
			#object_listing=paginator.get_page(page)
			return qs
		return Rhemadb.objects.none()