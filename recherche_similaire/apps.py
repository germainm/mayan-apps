import logging

from django.utils.translation import gettext_lazy as _

from mayan.apps.app_manager.apps import MayanAppConfig

logger = logging.getLogger(name=__name__)


class RechercheSimilaireConfig(MayanAppConfig):
    has_rest_api = True
    app_namespace = 'recherche_similaire'
    app_url = 'recherche_similaire'
    name = 'mayan.apps.recherche_similaire'
    verbose_name = _(message='Recherche similaire')

    def ready(self):
        super().ready()

        from mayan.apps.acls.classes import ModelPermission
        from mayan.apps.documents.models.document_models import Document
        from .permissions import permission_similaire_view

        ModelPermission.register(
            model=Document,
            permissions=(permission_similaire_view,)
        )

        from mayan.apps.common.menus import menu_object
        from .links import link_document_similaires

        menu_object.bind_links(
            links=(link_document_similaires,),
            sources=(Document,)
        )

        logger.debug('App recherche_similaire prête.')
