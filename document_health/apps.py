import logging
from django.utils.translation import gettext_lazy as _
from mayan.apps.app_manager.apps import MayanAppConfig

logger = logging.getLogger(name=__name__)


class DocumentHealthConfig(MayanAppConfig):
    app_namespace = 'document_health'
    app_url = 'document_health'
    name = 'mayan.apps.document_health'
    verbose_name = _(message='Qualité des documents')

    def ready(self):
        super().ready()

        from mayan.apps.common.menus import menu_tools
        from .links import link_document_health

        menu_tools.bind_links(
            links=(link_document_health,)
        )

        logger.debug('App document_health prête.')
