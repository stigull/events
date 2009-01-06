#coding: utf-8
import unittest
from datetime import datetime

from django.contrib.auth.models import User

from events.models import Event, EventType
    #name = models.CharField('Heiti', max_length = 50)
    #slug = models.SlugField(unique_for_date='starts', editable = False, blank = True)
    #location = models.CharField('Staðsetning', max_length = 150)
    #event_type = models.ForeignKey(EventType, verbose_name='Tag')

    #starts = models.DateTimeField('Hefst')
    #ends = models.DateTimeField('Lýkur')

    #info = models.TextField('Upplýsingar', blank = True, null = True)
    #info_html = models.TextField(editable = False, blank = True, null = True)

    #arrive_when = models.DateTimeField('Mæting hvenær', null = True, blank = True)
    #arrive_where = models.CharField('Mæting hvert', null = True, max_length = 150, blank = True)

    #registration_starts = models.DateTimeField('Skráning hefst')
    #registration_limit = models.IntegerField('Takmarka skráningu',
            #blank = True, default = 0, choices = REGISTRATION_LIMIT_CHOICES)

class EventHasPassedTestCase(unittest.TestCase):
    def setUp(self):
        self.event = Event("Name", "name", "Location", EventType("Type"),
                        starts = datetime(2009, 1, 6, 12, 0),
                        ends = datetime(2009, 1, 6, 12, 42),
                        registration_starts = datetime(2009, 1, 6, 11, 30),
                        registration_limit = 0)

    def test_has_not_passed(self):
        now = datetime(2009,1,6, 12,30)
        self.assertEqual(self.event.has_passed(now), False)

    def test_has_not_passed_last_minute(self):
        now = datetime(2009,1,6, 12,42)

        self.assertEqual(self.event.has_passed(now), False)

    def test_has_passed(self):
        now = datetime(2009,1,6, 12,50)
        self.assertEqual(self.event.has_passed(now), True)

class EventRegistrationTestCase(unittest.TestCase):
    def setUp(self):
        self.event = Event("Name", "name", "Location", EventType("Type"),
                        starts = datetime(2009, 1, 6, 12, 0),
                        ends = datetime(2009, 1, 6, 12, 42),
                        registration_starts = datetime(2009, 1, 6, 11, 30),
                        registration_limit = 0)

    def test_registration_has_not_started(self):
        now = datetime(2009, 1, 6, 11, 0)
        self.assertEqual(self.event.registration_has_started(now), False)

    def test_registration_has_started_first_minute(self):
        now = datetime(2009, 1, 6, 11, 30)
        self.assertEqual(self.event.registration_has_started(now), True)

    def test_registration_has_started(self):
        now = datetime(2009, 1, 6, 11, 31)
        self.assertEqual(self.event.registration_has_started(now), True)

class EventRegistrationHasRegistrationLimitTestCase(unittest.TestCase):
    def test_has_registration_limit(self):
        event = Event("Name", "name", "Location", EventType("Type"),
                        starts = datetime(2009, 1, 6, 12, 0),
                        ends = datetime(2009, 1, 6, 12, 42),
                        registration_starts = datetime(2009, 1, 6, 11, 30),
                        registration_limit = 1)
        self.assertEqual(event.has_registration_limit(), True)

    def test_has_not_registration_limit(self):
        event = Event("Name", "name", "Location", EventType("Type"),
                        starts = datetime(2009, 1, 6, 12, 0),
                        ends = datetime(2009, 1, 6, 12, 42),
                        registration_starts = datetime(2009, 1, 6, 11, 30),
                        registration_limit = 0)
        self.assertEqual(event.has_registration_limit(), False)

class EventAddAttendeeTestCase(unittest.TestCase):
    def test_add_attendee(self):
        event_type = EventType.objects.create(typename = "Type")
        event = Event.objects.create(name = "Name", slug = "name", location = "Location",
                    event_type = event_type,
                    starts = datetime(2009, 1, 6, 12, 0),
                    ends = datetime(2009, 1, 6, 12, 42),
                    registration_starts = datetime(2009, 1, 6, 11, 30),
                    registration_limit = 0)
        user = User.objects.create(username = "1")
        user_2 = User.objects.create(username = "2")

        event.add_user_to_list_of_attendees(user)
        self.assertEqual(event.get_attending_users(),[user])

        event.add_user_to_list_of_attendees(user_2)
        self.assertEqual(event.get_attending_users(),[user, user_2])


