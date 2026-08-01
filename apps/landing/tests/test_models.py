import uuid

from django.test import TestCase

from apps.landing.models import Lead

from .factories import LeadFactory


class LeadModelTests(TestCase):
    def test_pk_is_uuid(self):
        lead = LeadFactory()
        self.assertIsInstance(lead.pk, uuid.UUID)

    def test_str(self):
        lead = LeadFactory(name='Ana Pérez', email='ana@empresa.com')
        self.assertEqual(str(lead), 'Ana Pérez <ana@empresa.com>')

    def test_created_at_auto_set(self):
        lead = LeadFactory()
        self.assertIsNotNone(lead.created_at)

    def test_ordering_newest_first(self):
        older = LeadFactory()
        newer = LeadFactory()
        self.assertEqual(list(Lead.objects.all()), [newer, older])

    def test_company_and_message_optional(self):
        lead = LeadFactory(company='', message='', service_interest='')
        lead.full_clean()
