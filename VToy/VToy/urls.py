from django.conf.urls import patterns, include, url
from views import hello, rtthreadtext, rtthreadaudio, rtthreadaudiostream, handleWXHttpRequest

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^vtoy/admin/', include(admin.site.urls)),
    url(r'^vtoy/hello/$', hello),
	url(r'^vtoy/text/$', rtthreadtext),
    url(r'^vtoy/audio/$',rtthreadaudio),
    url(r'^vtoy/$', handleWXHttpRequest), # for weixin handler
)
