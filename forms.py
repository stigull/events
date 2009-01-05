#coding: utf-8
import django.forms as forms
from django.contrib.auth.models import User

from events.models import Event, EventRegistration

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

class ModelField(forms.Field):

    def __init__(self, model, required = True, label =None , initial = None, widget = forms.HiddenInput, help_text = None):
        super(ModelField, self).__init__(required = required, label = label,
                                            initial = initial, widget = widget, help_text = help_text)
        self.model = model

    def clean(self, instance_id):
        return self.model.objects.get(pk = instance_id)




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
