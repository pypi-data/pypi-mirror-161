from rest_framework import serializers
from expiry_addon.models import ResourceExpiryPolicy


class ResourceExpiryPolicySerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = ResourceExpiryPolicy
        fields = "__all__"


class ResourceExpiryPolicySourceAdder:
    # Class is used to generically add data to the existing serializers
    # in the Resource Locker
    extend_serializer = "LockableResourceSerializer"  # Name this the same name of the class to extend it's serializer
    serializer = (
        ResourceExpiryPolicySerializer  # The actual reference to the Serializer class
    )
    read_only = True  # In order to avoid complexity, better to use read-only fields when extending the serializers
    source = "resourceexpirypolicy"  # Should be the same name as the OneToOneRef (
