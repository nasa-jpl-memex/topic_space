from django.conf.urls import patterns, url

from topic_space_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
    url(r'^get_wordcloud/(?P<request_id>\d+)/$', views.get_wordcloud, name='get_wordcloud'),
)
