from rest_framework import serializers

from {{path_to_app}}.models import {{MainClass}}


class {{MainClass}}Serializer(serializers.ModelSerializer):
    """{{docs}}"""

    class Meta(object):
        model = {{MainClass}}
        fields = {{list_main_fields}}


class {{MainClass}}Serializer(serializers.Serializer):
    """{{docs}}"""

