from django.test import SimpleTestCase

from apps.landing import content
from apps.landing.forms import LeadForm


def valid_data(**overrides):
    data = {
        'name': 'Ana Pérez',
        'email': 'ana@empresa.com',
        'company': 'Empresa SA',
        'service_interest': 'agentes-outbound',
        'message': 'Quiero automatizar mi prospección.',
        'website': '',
    }
    data.update(overrides)
    return data


class LeadFormTests(SimpleTestCase):
    def test_valid_data(self):
        form = LeadForm(data=valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_name_required(self):
        form = LeadForm(data=valid_data(name=''))
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_email_required_and_valid(self):
        form = LeadForm(data=valid_data(email=''))
        self.assertFalse(form.is_valid())
        form = LeadForm(data=valid_data(email='no-es-un-email'))
        self.assertFalse(form.is_valid())

    def test_optional_fields_can_be_empty(self):
        form = LeadForm(data=valid_data(company='', service_interest='', message=''))
        self.assertTrue(form.is_valid(), form.errors)

    def test_honeypot_filled_is_invalid(self):
        form = LeadForm(data=valid_data(website='http://spam.example'))
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_service_choices_track_content(self):
        choices = dict(LeadForm().fields['service_interest'].choices)
        for service in content.SERVICES:
            self.assertIn(service.slug, choices)
        self.assertIn('otro', choices)
