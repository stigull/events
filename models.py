#coding: utf-8
from datetime import datetime

from markdown import markdown

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from utils.stringformatting import slugify


#from stigull.standard.functions import getReadableDateTime
#from stigull.settings import MONTHS, getDayOfWeek

REGISTRATION_LIMIT_CHOICES = [(0, u"Engin takmörk")] + zip(range(1,100), range(1,100))

class EventType(models.Model):
    typename = models.CharField('Tag', max_length = 40)

    class Meta:
        verbose_name = 'Tegund af atburði'
        verbose_name_plural = 'Tegundir af afburðum'

    def __unicode__(self):
        return self.typename

class EventGetManager(models.Manager):
    def getEvents(self, date ):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT *
            FROM events_event e
            WHERE split_part(e.starts, ' ', 1) <= '%(date)s'
            AND '%(date)s' <= split_part(e.ends, ' ', 1)""" % {'date' :"%d-%02d-%02d" % (date.year, date.month, date.day) })
        result_list = []
        for row in cursor.fetchall():
            p = self.model(id = row[0], name = row[1], location = row[2], type = EventType.objects.get(id = row[3]), starts = row[4], ends = row[5], info = row[6], arrive_when = row[7], arrive_where = row[8], registration_starts = row[9], registration_limit = row[10])
            result_list.append(p)
        return result_list

class Event(models.Model):
    name = models.CharField('Heiti', max_length = 50)
    slug = models.SlugField(unique_for_date='starts', editable = False, blank = True)
    location = models.CharField('Staðsetning', max_length = 150)
    event_type = models.ForeignKey(EventType, verbose_name='Tag')

    starts = models.DateTimeField('Hefst')
    ends = models.DateTimeField('Lýkur')

    info = models.TextField('Upplýsingar', blank = True, null = True)
    info_html =models.TextField(editable = False, blank = True, null = True)

    arrive_when = models.DateTimeField('Mæting hvenær', null = True, blank = True)
    arrive_where = models.CharField('Mæting hvert', null = True, max_length = 150, blank = True)

    registration_starts = models.DateTimeField('Skráning hefst')
    registration_limit = models.IntegerField('Takmarka skráningu',
            blank = True, default = 0, choices = REGISTRATION_LIMIT_CHOICES)

    class Meta:
        verbose_name = "Atburður"
        verbose_name_plural = "Atburðir"
        ordering = ['-starts']

    def __unicode__(self):
        return "%s: %s" % (self.name, self.location)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.info != "":
            self.info_html = markdown(self.info)
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return ('event_details', (), { 'event_id': self.id, 'event_slug': self.slug })
    get_absolute_url = models.permalink(get_absolute_url)

    def get_registrations(self):
        return EventRegistration.objects.filter(event = self)

    def has_passed(self):
        return datetime.now() >= self.ends

    def get_has_passed_css_class(self):
        if self.has_passed():
            return "has-passed"
        else:
            return ""

    def registration_has_started(self):
        return self.registration_starts <= datetime.now()

    def has_attending_users(self):
        return self.get_registrations().count() > 0

    def has_registration_limit(self):
        return self.registration_limit > 0

    def is_full(self):
        if self.registration_limit == 0:
            return False
        else:
            return self.get_registrations().count() >= self.registration_limit

    def add_user_to_list_of_attendees(self, user):
        registration = EventRegistration(user = user, event = self)
        registration.save()

    def remove_user_from_list_of_attendees(self, user):
        registration = EventRegistration.objects.get(user = user, event = self)
        registration.delete()

    def user_is_attending(self, user):
        if user.is_authenticated():
            return self.get_registrations().filter(user = user).count() == 1
        else:
            return False

    def get_number_of_attendees(self):
        nr_of_attendees = self.get_registrations().count()
        if not self.has_registration_limit() or nr_of_attendees <= self.registration_limit:
            return nr_of_attendees
        else:
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
            self.time_registered = datetime.now()
        super(EventRegistration, self).save(*args, **kwargs)


