import datetime
from django.db import models
from lockable_resource.models import LockableResource
from django.utils.timezone import utc


class ResourceExpiryPolicy(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    lockable_resource = models.OneToOneField(LockableResource, on_delete=models.PROTECT)
    expiry_hour = models.IntegerField(default=0)
    current_expiry_date = models.DateTimeField(null=True, default=None, blank=True)

    @property
    def is_expired(self):
        if self.lockable_resource.is_locked and self.current_expiry_date:
            return self.current_expiry_date < datetime.datetime.utcnow().replace(
                tzinfo=utc
            )

    def __str__(self):
        return f"{self.name}"

    # Meta Class
    class Meta:
        # Override verbose name plural to get nicer description in Admin Page:
        verbose_name_plural = "Resource Expiry Policies"
