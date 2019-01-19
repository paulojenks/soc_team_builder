from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from . import views

app_name='accounts'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'sign_in/$', views.SignInView.as_view(), name='sign_in'),
    url(r'sign_up/$', views.RegisterView.as_view(), name='sign_up'),
    url(r'sign_out/$', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='sign_out'),
    url(r'profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'profile/edit/$', views.ProfileUpdateView.as_view(), name='edit_profile'),
    url(r'project/new/$', views.ProjectCreateView.as_view(), name='project_new'),
    url(r'project/(?P<pk>\d+)/edit/$', views.ProjectUpdateView.as_view(), name='project_edit'),
    url(r'project/(?P<pk>\d+)/$', views.ProjectView.as_view(), name='project'),
    url(r'project/(?P<pk>\d+)/delete/$', views.ProjectDeleteView.as_view(), name='project_delete'),
    url(r'applications/(?P<pk>\d+)/$', views.ApplicationUpdateView.as_view(), name='application_detail'),
    url(r'applications/(?P<pk>\d+)/delete/$', views.delete_application, name='application_delete'),
    url(r'applications/$', views.ApplicationView.as_view(), name='applications'),
    url(r'applications/new/(?P<pk>\d+)/$', views.ApplicationCreateView.as_view(), name='application_new'),
    url(r'delete_skill/(?P<pk>\d+)/$', views.delete_skill, name='skill_delete'),
    url(r'delete_position/(?P<pk>\d+)/$', views.delete_position, name='position_delete'),
    url(r'search/$', views.search, name='search'),
    url(r'sort_by_skill/(?P<skillz>\w+)/$', views.sort_by_skill, name='sort')
]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)