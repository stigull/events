#coding: utf-8
from django import template
from django.core.urlresolvers import reverse

from events.forms import EventRegistrationForm, EventUnregistrationForm

register = template.Library()

def render_form(Form, urlname, label, name):
    def render_custom_form(user, event):
        context = {'label': label, 'url': reverse(urlname)}
        context['form'] = Form(initial = {'user': user.id, 'event': event.id })
        return context
    render_custom_form.func_name = name
    return render_custom_form

render_registration_form = render_form(EventRegistrationForm, 'event_attend', u'Skrá á atburð', "render_registration_form")
register.inclusion_tag('events/forms/generic_form.html')(render_registration_form)

render_unregistration_form = render_form(EventUnregistrationForm, 'event_unattend', u'Afskrá af atburði', "render_unregistration_form")
register.inclusion_tag('events/forms/generic_form.html')(render_unregistration_form)

    #@register.inclusion_tag('events/latest_events.html', takes_context = True)
    #def getLatestEvents(context):
    #latestEvents = context['event'] = Event.objects.filter(starts__gte = datetime.now()).order_by('starts')
    #if latestEvents.count() > 3:
        #latestEvents = latestEvents[:3]
    #context['latest_events'] = []
    #for event in latestEvents:
        #context['latest_events'].append( (event, event.userIsRegistered(context['user'])))
    #context['userIsAuthenticated'] = context['user'].is_authenticated()
    #return context

    #@register.inclusion_tag('events/latest_events_snerti.html', takes_context = True)
    #def getLatestEventsSnerti(context):
    #latestEvents = context['event'] = Event.objects.filter(starts__gte = datetime.now()).order_by('starts')
    #if latestEvents.count() > 3:
        #latestEvents = latestEvents[:3]
    #context['latest_events'] = []
    #for event in latestEvents:
        #context['latest_events'].append((event, event.userIsRegistered(context['beer_user'].user)))
    #return context