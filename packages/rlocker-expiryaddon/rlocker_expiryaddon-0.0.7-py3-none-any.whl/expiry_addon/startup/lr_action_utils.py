import expiry_addon.constants as const
from datetime import timedelta
from django.contrib import messages
from lockable_resource.action_manager import LRActionManager

EXTENDED_SUPPORTED_ACTIONS = [const.ACTION_MODIFY_EXPIRY]


class LRActionModifyExpiry(LRActionManager):
    def complete_action(self):
        add_expiry_hours = int(
            self.request.POST.get(f"add-expiry-hours-{self.r_lock_id}")
        )
        self.r_lock_obj.resourceexpirypolicy.current_expiry_date += timedelta(
            hours=add_expiry_hours
        )
        self.r_lock_obj.resourceexpirypolicy.save()
        messages.info(
            self.request,
            message=f"{self.r_lock_obj.name} expiry date is updated to: {self.r_lock_obj.resourceexpirypolicy.current_expiry_date}. "
            f"Added hours: {add_expiry_hours}",
        )
