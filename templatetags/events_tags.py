#coding: utf-8
from datetime import datetime

from django import template
from django.core.urlresolvers import reverse

from events.forms import EventRegistrationForm, EventUnregistrationForm
from events.models import validator_registry, Event

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

def check_if_user_can_attend(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError("'%s' tag takes exactly four arguments" % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError("third argument to '%s' tag must be 'as'" % bits[0])
    return CanAttendNode(bits[1], bits[3])

check_if_user_can_attend = register.tag(check_if_user_can_attend)


class CanAttendNode(template.Node):
    def __init__(self, user, varname):
        self.user = template.Variable(user)
        self.varname = varname

    def render(self, context):
        validator = validator_registry.get_validator()
        try:
            context[self.varname] = validator.can_attend(self.user.resolve(context))
        except template.VariableDoesNotExist:
            context[self.varname] = False
        return ''

def check_if_user_is_attending(parser, token):
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError("'%s' tag takes exactly four arguments" % bits[0])
    if bits[3] != 'as':
        raise TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    return IsAttendingNode(bits[1], bits[2], bits[4])

check_if_user_is_attending = register.tag(check_if_user_is_attending)


class IsAttendingNode(template.Node):
    def __init__(self, user, event, varname):
        self.user = template.Variable(user)
        self.event = template.Variable(event)
        self.varname = varname

    def render(self, context):
        try:
            user = self.user.resolve(context)
            event = self.event.resolve(context)
        except template.VariableDoesNotExist:
            context[self.varname] = False
        else:
            if event is not None and user.is_authenticated():
                context[self.varname] = event.user_is_attending(user)
            else:
                context[self.varname] = False
        return ''

def get_latest_events(context):
    latest_events = Event.objects.filter(ends__gte = datetime.now())
    if latest_events.count() > 3:
        latest_events = latest_events[:3]
    context['latest_events'] = latest_events
    return context
get_latest_events = register.inclusion_tag('events/latest_events.html', takes_context = True)(get_latest_events)

    #@register.inclusion_tag('events/latest_events.html', takes_context = True)
    #def getLatestEvents(context):


    #@register.inclusion_tag('events/latest_events_snerti.html', takes_context = True)
    #def getLatestEventsSnerti(context):
    #latestEvents = context['event'] = Event.objects.filter(starts__gte = datetime.now()).order_by('starts')
    #if latestEvents.count() > 3:
        #latestEvents = latestEvents[:3]
    #context['latest_events'] = []
    #for event in latestEvents:
        #context['latest_events'].append((event, event.userIsRegistered(context['beer_user'].user)))
    #return context
