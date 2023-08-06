# This file loads up for ONE TIME once the application
# is being recognized as an INSTALLED_APP (INSTALLED_ADDON)
# Use this file to add code that should be executed first time

import expiry_addon.constants as const
from lockable_resource.action_manager import LRActionObjectsHandler, SUPPORTED_ACTIONS
from expiry_addon.startup import lr_action_utils
from expiry_addon.apps import ExpiryAddonConfig


def main():
    print(f"The Addon {ExpiryAddonConfig.name} is recognized!")
    SUPPORTED_ACTIONS.extend(lr_action_utils.EXTENDED_SUPPORTED_ACTIONS)
    a = LRActionObjectsHandler()
    a.add_supported_action_object_pair(
        key=const.ACTION_MODIFY_EXPIRY, value=lr_action_utils.LRActionModifyExpiry
    )
