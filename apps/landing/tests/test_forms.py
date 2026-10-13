from django.test import SimpleTestCase

from apps.landing import content
from apps.landing.forms import ContactForm, LeadForm
from apps.legal import content as legal_content


def valid_data(**overrides):
    data = {
        'name': 'Ana Pérez',
        'email': 'ana@empresa.com',
        'company': 'Empresa SA',
        'service_interest': 'agentes-inbound',
        'message': 'Quiero automatizar mi prospección.',
        'website': '',
        'privacy': 'on',
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

    def test_honeypot_field_is_hidden_and_optional(self):
        # El descarte del honeypot lo hace la vista (éxito falso); el form solo
        # debe renderizar el campo oculto sin exigirlo.
        form = LeadForm()
        self.assertFalse(form.fields['website'].required)
        self.assertIn('hp-field', form.fields['website'].widget.attrs['class'])

    def test_message_over_2000_chars_is_invalid(self):
        form = LeadForm(data=valid_data(message='x' * 2001))
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_message_of_2000_chars_is_valid(self):
        form = LeadForm(data=valid_data(message='x' * 2000))
        self.assertTrue(form.is_valid(), form.errors)

    def test_privacy_checkbox_is_required(self):
        data = valid_data()
        del data['privacy']
        form = LeadForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['privacy'], [legal_content.FORM_CONSENT['required_message']]
        )

    def test_contact_form_also_requires_privacy(self):
        form = ContactForm(data={
            'product': 'diagnostico', 'name': 'Ana Pérez', 'email': 'ana@empresa.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('privacy', form.errors)

    def test_service_choices_track_content(self):
        choices = dict(LeadForm().fields['service_interest'].choices)
        for service in content.SERVICES:
            self.assertIn(service.slug, choices)
        self.assertIn('otro', choices)
