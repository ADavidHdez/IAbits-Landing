import factory

from apps.landing.models import Lead


class LeadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lead

    name = factory.Faker('name', locale='es_ES')
    email = factory.Faker('email')
    company = factory.Faker('company', locale='es_ES')
    service_interest = 'agentes-outbound'
    message = factory.Faker('sentence', locale='es_ES')
