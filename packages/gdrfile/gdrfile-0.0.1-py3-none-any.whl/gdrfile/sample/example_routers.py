from django.utils.translation import gettext_lazy as _
from drf_nova_router.api_router import ApiRouter
from rest_framework.routers import APIRootView

from {{path_to_app}}.api.views import (
    {{MainClass}}ViewSet,
)


class {{AppName}}APIRootView(APIRootView):
    """Корневой view для app."""

    __doc__ = _('Приложение {{AppName}}')
    name = _('{{app_name}}')


router = ApiRouter()

router.APIRootView = {{AppName}}APIRootView
router.register('{{main-class}}s', {{MainClass}}ViewSet, '{{main-class}}s')
