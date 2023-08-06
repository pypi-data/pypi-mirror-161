from expiry_addon import views, run_startup
from django.urls import path

# In order to call to those as `expiry_addon:view_name` we need this
app_name = "expiry_addon"

urlpatterns = []


# Use this section to call to a code that runs one time once the application loads:
run_startup.main()
