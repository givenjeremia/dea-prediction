# yourapp/management/commands/create_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        groups_data = [
            {'name': 'Super Admin'},
            {'name': 'Admin'}
        ]

        for group_data in groups_data:
            group, created = Group.objects.get_or_create(name=group_data['name'])
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group.name}" created successfully.'))
            else:
                self.stdout.write(self.style.WARNING(f'Group "{group.name}" already exists.'))


        self.stdout.write(self.style.SUCCESS('Groups creation complete.'))
