from django.conf.urls import patterns, include, url
from views import hello, rtthreadtext, rtthreadaudio, rtthreadaudiostream

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', hello),
	url(r'^rtthreadtext/$', rtthreadtext),
    url(r'^rtthreadaudio/$',rtthreadaudio),
    url(r'^rtthreadaudiostream/$',rtthreadaudiostream),
)
