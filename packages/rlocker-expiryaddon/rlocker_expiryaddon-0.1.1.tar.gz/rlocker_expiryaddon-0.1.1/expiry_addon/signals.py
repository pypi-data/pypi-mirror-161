from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from expiry_addon.models import ResourceExpiryPolicy
from lockable_resource.models import LockableResource


@receiver(post_save, sender=ResourceExpiryPolicy)
def generate_field_values_if_empty(sender, instance, created, **kwargs):
    """
    For some fields we'd like to generate values if they left empty.
    Using blank=true and null=true is effective, but the default value we'd
        like to generate, is based on another IntegerField which is required
    For Example:
    ResourceExpiryPolicy(
        name="",
        expiry_hour=24,
        lockable_resource=1TO1Field('some_resource_1')
    )
    We'd like to have this after post_save():
        ResourceExpiryPolicy(
        name="H24-some-resource-1",
        expiry_hour=24,
        lockable_resource=1TO1Field('some_resource_1')
    )
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return: None
    """
    if created:
        if not instance.name:
            instance.name = f"H{instance.expiry_hour}-{instance.lockable_resource.name}"
            instance.save()

    if not created:
        pass


@receiver(post_save, sender=LockableResource)
def do_actions_after_locked_resource(sender, instance, created, **kwargs):
    """
    post_save is being called everytime the object is being saved!
    REMEMBER: The save method could be called more than once for an object.
    Why ? Because each modification on a specific object happens only AFTER the save method
    So the post_save signal is triggered after every modification!
    """
    if created:
        return
    if not created:
        # If instance has locked time, it means a resource is just locked and locked time is not None
        if instance.resourceexpirypolicy:
            if (
                instance.locked_time
                and not instance.resourceexpirypolicy.current_expiry_date
            ):
                current_expiry_date = instance.locked_time
                current_expiry_date += timedelta(
                    hours=instance.resourceexpirypolicy.expiry_hour
                )
                instance.resourceexpirypolicy.current_expiry_date = current_expiry_date
                instance.resourceexpirypolicy.save()
                print(
                    f"{instance.name} will expired in {instance.resourceexpirypolicy.current_expiry_date}"
                )

            if not instance.locked_time:
                instance.resourceexpirypolicy.current_expiry_date = None
                instance.resourceexpirypolicy.save()
