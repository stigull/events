#coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from events.models import EventType, Event, EventRegistration
from events.forms import EventForm

def get_number_of_attendees(event):
    return event.get_number_of_attendees()
get_number_of_attendees.short_description = _(u"Fjöldi skráðra")

class EventAdmin(admin.ModelAdmin):
    form = EventForm
    fieldsets = (
        (_(u"Almennt"), {
            'fields': ('name', 'location','event_type', 'starts', 'ends')
        }),
        (_(u"Nánari upplýsingar"), {
            'fields': ('info',)
        }),
        (_(u"Mæting"), {
            'fields': ('arrive_when', 'arrive_where',)
        }),
        (_(u"Skráning"), {
            'fields': ('registration_starts', 'registration_limit')
        }),
    )

    list_display = ('name',  'location', 'starts',  'ends', 'registration_limit', get_number_of_attendees)

class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('time_registered',  'event', 'user', )

admin.site.register(EventType)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(Event, EventAdmin)