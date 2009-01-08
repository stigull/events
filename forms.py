#coding: utf-8
import django.forms as forms
from django.contrib.auth.models import User

from events.models import Event, EventRegistration
from utils.djangoutils import ModelField

class EventForm(forms.ModelForm):
    def clean(self):
        data = self.cleaned_data
        if 'starts' in data and 'ends' in data:
            if data['starts'] >= data['ends']:
                raise forms.ValidationError(u'Atburðinum má ekki ljúka áður en hann hefst.')

        if 'starts' in data and 'registration_starts' in data :
            if data['starts'] <= data['registration_starts']:
                raise forms.ValidationError(u"Skráning í atburðinn verður að hefjast áður en að atburðurinn sjálfur hefst")

        if 'arrive_when' in data and data['arrive_when'] is not None:
            if not 'arrive_where' in data or 'arrive_where' in data and data['arrive_where'] == u"":
                raise forms.ValidationError(u"Ef mætingartími er skráður þá verður að skrá mætingarstað")

        return self.cleaned_data

    class Meta:
        model = Event


class EventRegistrationForm(forms.Form):
    event = ModelField(Event)
    user = ModelField(User)

    def process(self):
        event = self.cleaned_data['event']
        user = self.cleaned_data['user']
        event.add_user_to_list_of_attendees(user)

class EventUnregistrationForm(EventRegistrationForm):

    def process(self):
        event = self.cleaned_data['event']
        user = self.cleaned_data['user']
        event.remove_user_from_list_of_attendees(user)
