from rest_framework import serializers

# Sort of data to expect
from .models import Category, Channel, Server


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"


# serializers has a ModelSerializer which enables us to utilize the model information from django to quickly create a serializer.
class ServerSerializer(serializers.ModelSerializer):
    # serializer method field, field class that allows you to add any custom methods to generate a field of value. We will need to pass in data, so we will also have to create an associated num_members function to handle this.
    num_members = serializers.SerializerMethodField()

    # Anytime any of the queries utilize the ServerSerializer is also going to grab the Channels associated to the servers it does that because we have the foreign key key relationship between the Channel table and the Server table. And here we have utilized the same related name specified in models.py under the Channel Model. While we could use a seperate filter in views.py to retrieve associated Channels, we are consider Channels to be nothing more than a servers associated data, so why use a seperata filter. Hence, we have used a hardcode approach.
    channel_server = ChannelSerializer(many=True)

    # What model we are using and fields we want serialized and sent to frontend
    class Meta:
        model = Server
        exclude = ("member",)

    def get_num_members(Self, obj):
        # this num_members refers to num_members data returned from views.py queryset.
        if hasattr(obj, "num_members"):
            return obj.num_members
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # reference to the key 'with_num_members' boolean value
        num_members = self.context.get("num_members")
        if not num_members:
            data.pop("num_members", None)
        return data
