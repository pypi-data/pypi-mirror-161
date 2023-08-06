from rest_framework.viewsets import ModelViewSet

from {{path_to_app}}.api.serializers import {{MainClass}}Serializer
from {{path_to_app}}.models import {{MainClass}}


class {{MainClass}}ViewSet(ModelViewSet):
    """{{docs}}"""

    queryset = {{MainClass}}.objects.all()
    serializer_class = {{MainClass}}Serializer
    ordering_fields = {{list_main_fields}}
    search_fields = {{list_main_fields}}
