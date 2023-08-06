from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.viewsets import ModelViewSet
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from {{path_to_app}}.api.serializers import AccountSerializer
from {{path_to_app}}.models import Account

class {{MainClass}}ViewSet(
    NestedViewSetMixin,
    AutoPermissionViewSetMixin,
    ModelViewSet,
):
    """{{docs}}"""

    queryset = {{MainClass}}.objects.all()
    serializer_class = {{MainClass}}Serializer
    ordering_fields = {{list_main_fields}}
    search_fields = {{list_main_fields}}
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        'list': 'list',
        'metadata': None,
    }
