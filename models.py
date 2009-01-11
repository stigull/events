#coding: utf-8
import datetime

from markdown2 import markdown

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from utils.stringformatting import slugify

REGISTRATION_LIMIT_CHOICES = [(0, u"Engin takmörk")] + zip(range(1,100), range(1,100))

class ValidatorRegistry(object):

    def __init__(self):
        self.validator = RegistrationValidator()

    def add_validator(self, validator):
        assert issubclass(validator.__class__, RegistrationValidator)
        self.validator = validator

    def get_validator(self):
        return self.validator


class RegistrationValidator(object):
    def can_attend(self, user):
        return user.is_authenticated()


validator_registry = ValidatorRegistry()


class EventType(models.Model):
    typename = models.CharField('Tag', max_length = 40)

    class Meta:
        verbose_name = 'Tegund af atburði'
        verbose_name_plural = 'Tegundir af afburðum'

    def __unicode__(self):
        return self.typename

class EventGetManager(models.Manager):
    def get_events_for_day(self, date):
        start_of_day = datetime.datetime.combine(date, datetime.time(0,0))
        end_of_day = datetime.datetime.combine(date, datetime.time(23,59,59))
        starts_in_day_query = models.Q(starts__gte = start_of_day, starts__lte = end_of_day)
        ends_in_day_query = models.Q(ends__gte = start_of_day, ends__lte = end_of_day)
        overlaps_day_query = models.Q(starts__lte = start_of_day, ends__gte = end_of_day)
        return self.get_query_set().filter(starts_in_day_query | ends_in_day_query | overlaps_day_query)

class Event(models.Model):
    name = models.CharField('Heiti', max_length = 50)
    slug = models.SlugField(unique_for_date='starts', editable = False, blank = True)
    location = models.CharField('Staðsetning', max_length = 150)
    event_type = models.ForeignKey(EventType, verbose_name='Tag')

    starts = models.DateTimeField('Hefst')
    ends = models.DateTimeField('Lýkur')

    info = models.TextField('Upplýsingar', blank = True, null = True)
    info_html = models.TextField(editable = False, blank = True, null = True)

    arrive_when = models.DateTimeField('Mæting hvenær', null = True, blank = True)
    arrive_where = models.CharField('Mæting hvert', null = True, max_length = 150, blank = True)

    registration_starts = models.DateTimeField('Skráning hefst')
    registration_limit = models.IntegerField('Takmarka skráningu', default = 0, choices = REGISTRATION_LIMIT_CHOICES)

    objects = EventGetManager()

    class Meta:
        verbose_name = "Atburður"
        verbose_name_plural = "Atburðir"
        ordering = ['-starts']

    def __unicode__(self):
        if self.starts.date() != self.ends.date():
            return u"%s, %s - %s" % (self.name,
                            self.starts.strftime("%a %H:%M"),
                            self.ends.strftime("%a %H:%M"))
        else:
            return u"%s, %s - %s" % (self.name,
                            self.starts.strftime("%H:%M"),
                            self.ends.strftime("%H:%M"))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.info != "":
            self.info_html = markdown(self.info)
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return ('event_details', (), { 'event_id': self.id, 'event_slug': self.slug })
    get_absolute_url = models.permalink(get_absolute_url)

    def get_duration(self, date):
        start_of_day = datetime.datetime.combine(date, datetime.time(0,0))
        end_of_day = datetime.datetime.combine(date, datetime.time(23,59,59))

        starts_time = self.starts.strftime("%H:%M")
        ends_time = self.ends.strftime("%H:%M")
        if self.starts >= start_of_day and self.starts <= end_of_day:
            if self.ends >= start_of_day and self.ends <= end_of_day:
                return "%s - %s" % (starts_time, ends_time)
            else:
                return "%s - 23:59" % starts_time
        elif self.ends >= start_of_day and self.ends <= end_of_day:
            return "00:00 - %s" % ends_time
        elif self.starts <= start_of_day and self.ends >= end_of_day:
            return u"00:00 - 23:59"
        else:
            return ""

    def has_passed(self, now = None):
        if now is None:
            now = datetime.datetime.now()
        return now > self.ends

    def has_started(self, now = None):
        if now is None:
            now = datetime.datetime.now()
        return self.starts <= now

    def registration_has_started(self, now = None):
        if now is None:
            now = datetime.datetime.now()
        return self.registration_starts <= now

    def has_registration_limit(self):
        return self.registration_limit > 0

    def get_registrations(self):
        return EventRegistration.objects.filter(event = self)

    def has_attending_users(self):
        return self.get_registrations().count() > 0

    def add_user_to_list_of_attendees(self, user):
        registration = EventRegistration.objects.create(user = user, event = self)

    def remove_user_from_list_of_attendees(self, user):
        registration = EventRegistration.objects.get(user = user, event = self)
        registration.delete()

    def is_full(self):
        if self.registration_limit == 0:
            return False
        else:
            return self.get_registrations().count() >= self.registration_limit

    def user_is_attending(self, user):
        return self.get_registrations().filter(user = user).count() == 1

    def get_number_of_attendees(self):
        nr_of_attendees = self.get_registrations().count()
        if not self.has_registration_limit() or nr_of_attendees <= self.registration_limit:
            return nr_of_attendees
        else:
            #The event has a registration limit and then number of attendes is greater than the limit
            return self.registration_limit

    def get_formatted_number_of_attendees(self):
        if self.has_registration_limit():
            return "%d/%d" % (self.get_number_of_attendees(), self.registration_limit)
        else:
            return self.get_number_of_attendees()

    def get_attending_users(self):
        attending_users = [registration.user for registration in self.get_registrations()]
        if self.has_registration_limit():
            return attending_users[:min(self.registration_limit, len(attending_users))]
        else:
            return attending_users

    def has_waiting_list(self):
        return self.get_registrations().count() > self.registration_limit

    def get_waiting_list(self):
        attending_users = [registration.user for registration in self.get_registrations()]
        return attending_users[self.registration_limit:]

    def has_arrive_information(self):
        return self.arrive_when is not None and self.arrive_where != u""

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, verbose_name='Atburður')
    user = models.ForeignKey(User, verbose_name='Notandi')
    time_registered = models.DateTimeField()

    class Meta:
        verbose_name = 'Skráning á atburð'
        verbose_name_plural = 'Skráningar á atburði'
        ordering = ['time_registered', ]
        unique_together = ('event', 'user')

    def save(self, *args, **kwargs):
        if self.id is None and self.time_registered is None:
            self.time_registered = datetime.datetime.now()
        super(EventRegistration, self).save(*args, **kwargs)


