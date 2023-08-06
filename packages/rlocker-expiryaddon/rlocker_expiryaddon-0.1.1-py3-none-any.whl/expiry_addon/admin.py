from django.contrib import admin
from expiry_addon.models import ResourceExpiryPolicy


@admin.register(ResourceExpiryPolicy)
class ResourceExpiryPolicyAdmin(admin.ModelAdmin):
    list_display = [
        str(field).split(".")[-1] for field in ResourceExpiryPolicy._meta.get_fields()
    ]
    readonly_fields = [
        "is_expired",
    ]
    list_display.extend(readonly_fields)
