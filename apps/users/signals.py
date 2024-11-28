# # signals.py
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models import ActionLog
# from .middleware import get_current_user
# from django.contrib.auth.models import User

# @receiver(post_save)
# def log_create_update(sender, instance, created, **kwargs):
#     if sender == ActionLog:
#         return 

#     if not hasattr(instance, 'id'):
#         return

#     user = get_current_user()

#     if isinstance(user, User) and user.is_authenticated:
#         action = 'CREATE' if created else 'UPDATE'
#         ActionLog.objects.create(
#             user=user,
#             action=action,
#             model_name=sender.__name__,
#             object_id=instance.id,
#             details=(
#                 f"User dengan username '{user.username}' melakukan aksi {action} "
#                 f"pada {sender.__name__} pada bagian: {instance} dengan ID {instance.id}."
#             )
#         )
#     else:
#         print("Anonymous user action, no log created.")

# @receiver(post_delete)
# def log_delete(sender, instance, **kwargs):
#     if sender == ActionLog:
#         return

#     if hasattr(instance, 'id'): 
#         user = get_current_user()

#         if isinstance(user, User) and user.is_authenticated:
#             ActionLog.objects.create(
#                 user=user,
#                 action='DELETE',
#                 model_name=sender.__name__,
#                 object_id=instance.id,
#                 details=(
#                     f"User dengan username '{user.username}' melakukan aksi DELETE "
#                     f"pada {sender.__name__} pada bagian: {instance} dengan ID {instance.id}."
#                 )
#             )
#         else:
#             print("Anonymous user delete action, no log created.")
#     else:
#         print(f"Instance does not have an ID: {instance}")
