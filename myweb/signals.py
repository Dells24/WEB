# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from .models import Student

@receiver(post_save, sender=Student)
def notify_admin_new_student(sender, instance, created, **kwargs):
    if created:
        LogEntry.objects.log_action(
            user_id=1,  # Assuming admin has user_id=1; adjust accordingly
            content_type_id=ContentType.objects.get_for_model(instance).pk,
            object_id=instance.pk,
            object_repr=str(instance),
            action_flag=ADDITION,
            change_message=f'A new student "{instance.name}" with registration number "{instance.reg_no}" has been added.'
        )

