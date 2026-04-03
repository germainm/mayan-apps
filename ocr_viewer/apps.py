import logging
from django.utils.translation import gettext_lazy as _
from mayan.apps.app_manager.apps import MayanAppConfig

logger = logging.getLogger(name=__name__)


class OCRViewerConfig(MayanAppConfig):
    has_rest_api = True
    app_namespace = 'ocr_viewer'
    app_url = 'ocr_viewer'
    name = 'mayan.apps.ocr_viewer'
    verbose_name = _(message='OCR Viewer')

    _api_urls_registered = False

    def ready(self):
        super().ready()

        from mayan.apps.acls.classes import ModelPermission
        from mayan.apps.documents.models.document_models import Document
        from .permissions import permission_ocr_viewer_view

        ModelPermission.register(
            model=Document,
            permissions=(permission_ocr_viewer_view,)
        )

        from mayan.apps.common.menus import menu_object
        from .links import link_document_ocr_viewer

        menu_object.bind_links(
            links=(link_document_ocr_viewer,),
            sources=(Document,)
        )

        if not OCRViewerConfig._api_urls_registered:
            from mayan.apps.rest_api.urls import api_version_urls
            from .urls import api_urls as ocr_api_urls
            api_version_urls.extend(ocr_api_urls)
            OCRViewerConfig._api_urls_registered = True
            # Invalider le cache URLconf Django
            from django.urls import clear_url_caches
            clear_url_caches()

        logger.debug('App ocr_viewer prête.')
