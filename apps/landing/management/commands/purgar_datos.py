from django.core.management.base import BaseCommand

from apps.landing.retention import purge_expired


class Command(BaseCommand):
    help = 'Borra los leads y las conversaciones del chat que superan su plazo de conservación.'

    def handle(self, *args, **options):
        result = purge_expired()
        self.stdout.write(self.style.SUCCESS(
            f'Borrados {result["leads"]} leads y {result["chat_conversations"]} conversaciones del chat.'
        ))
