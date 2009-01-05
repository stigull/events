#coding: utf-8
from django.conf.urls.defaults import *

from events.views import show_events, process_registration
from events.forms import EventRegistrationForm, EventUnregistrationForm

urlpatterns = patterns('',
    url(r'^$', show_events, name = 'events_index'),
    url(r'^(?P<event_id>\d+)-(?P<event_slug>[^/]+)/$', show_events, name = 'event_details'),
    url(r'^skra-a-atburd/$', process_registration, name="event_attend", kwargs = {'Form': EventRegistrationForm} ),
    url(r'^afskra-af-atburdi/$', process_registration, name="event_unattend", kwargs = {'Form': EventUnregistrationForm }),
)