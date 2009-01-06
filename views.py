#coding: utf-8
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response

from events.models import Event
from events.forms import EventRegistrationForm


def show_events(request, event_id = None, event_slug = None, page = 1):
    context = {}

    if event_id is not None:
        context['event'] = get_object_or_404(Event, pk = int(event_id))
    else:
        try:
            context['event'] = Event.objects.filter(starts__gte = datetime.now())[0]
        except IndexError:
            context['event'] = None

    return render_to_response('events/events_base.html', context, context_instance = RequestContext(request))

def process_registration(request, Form):
    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            form.process()
            return HttpResponseRedirect(form.cleaned_data['event'].get_absolute_url())
    return HttpResponseRedirect(reverse('events_index'))


