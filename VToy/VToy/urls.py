from django.conf.urls import patterns, include, url
from views import hello, rtthreadtext, rtthreadaudio, rtthreadaudiostream, handleWXHttpRequest
from DeviceHttpHandler import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^vtoy/admin/', include(admin.site.urls)),
    url(r'^vtoy/hello/$', hello),
    url(r'^vtoy/text/$', rtthreadtext),
    url(r'^vtoy/audio/$',rtthreadaudio),
    url(r'^vtoy/messages/$', DeviceHttpHandler.handleQueryNewMsg),
    url(r'^vtoy/voice/(\d+)/$', DeviceHttpHandler.handleGetVoice),
    url(r'^vtoy/message/$', DeviceHttpHandler.handleSendMsg),
    url(r'^vtoy/$', handleWXHttpRequest), # for weixin handler
)
