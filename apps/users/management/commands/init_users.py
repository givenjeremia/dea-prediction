from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from management.models import Departements
from users.serializer import ProfileSerializer

class Command(BaseCommand):
    help = 'Create Users'

    def handle(self, *args, **options):
        # Create Super Admin
        # users_data = [
        #     {'username': 'superadmin', 'password': 'p@ssw0rd', 'groups': ['Super Admin']},
        # ]
        # for user_data in users_data:
        #     user, created = User.objects.get_or_create(username=user_data['username'])
        #     if created:
        #         user.set_password(user_data['password'])
        #         user.save()
        #         self.stdout.write(self.style.SUCCESS(f'User "{user.username}" created successfully.'))
        #     else:
        #         self.stdout.write(self.style.WARNING(f'User "{user.username}" already exists.'))

        #     for group_name in user_data['groups']:
        #         try:
        #             group = Group.objects.get(name=group_name)
        #             user.groups.add(group)
        #             self.stdout.write(self.style.SUCCESS(f'User "{user.username}" added to group "{group_name}".'))

        #         except Group.DoesNotExist:
        #             self.stdout.write(self.style.WARNING(f'Group "{group_name}" does not exist. Skipping user "{user.username}".'))


        # Create Admin By Departement
        departements = Departements.objects.filter(upt=True)
        for departement in departements:
            username_new = 'admin_' + departement.slug.replace("-", "_")
            name = 'ADMIN ' + departement.slug.replace("-", " ").upper()
            user, created = User.objects.get_or_create(
                username=username_new
            )
            if created:
                user.first_name = name
                user.set_password('p@ssw0rd')
                user.save()
                profile = {'departement': departement.id ,'unit_work': departement.unit_work_id,'user':user.id }
                serializer = ProfileSerializer(data=profile)
                if serializer.is_valid():
                    serializer.save()

                self.stdout.write(self.style.SUCCESS(f'User "{user.username}" created successfully.'))
            else:
                user.first_name = name
                user.set_password('p@ssw0rd')
                user.save()
                profile = {'departement': departement.id ,'unit_work': departement.unit_work_id,'user':user.id }
                serializer = ProfileSerializer(data=profile)
                if serializer.is_valid():
                    serializer.save()
                self.stdout.write(self.style.WARNING(f'User "{user.username}" already exists.'))

            for group_name in ['UPT']:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                    self.stdout.write(self.style.SUCCESS(f'User "{user.username}" added to group "{group_name}".'))
                except Group.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Group "{group_name}" does not exist. Skipping user "{user.username}".'))

        self.stdout.write(self.style.SUCCESS('User creation and group assignment complete.'))
