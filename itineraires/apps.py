# FICHIER : mayan/apps/itineraires/apps.py
# REMPLACEMENT dans la méthode ready()
#
# AVANT :
#   from mayan.apps.rest_api.urls import api_version_urls
#   from .urls import api_urls as itineraire_api_urls
#   if not any('itineraire' in str(u.pattern) for u in api_version_urls):
#       api_version_urls.extend(itineraire_api_urls)
#
# APRÈS : utiliser un flag de classe pour garantir l'idempotence

import logging

from django.utils.translation import gettext_lazy as _

from mayan.apps.app_manager.apps import MayanAppConfig

logger = logging.getLogger(name=__name__)


class ItinerairesConfig(MayanAppConfig):
    app_namespace = 'itineraires'
    app_url = 'itineraires'
    has_rest_api = True
    name = 'mayan.apps.itineraires'
    verbose_name = _(message='Itinéraires')

    # Flag de classe — évite la double registration si ready() est appelé
    # plusieurs fois (tests, rechargement à chaud, etc.)
    _api_urls_registered = False

    def ready(self):
        super().ready()

        from . import dependencies  # noqa

        from mayan.apps.acls.classes import ModelPermission
        from .models import Itineraire
        from .permissions import (
            permission_itineraire_view,
            permission_itineraire_create,
            permission_itineraire_delete,
        )

        ModelPermission.register(
            model=Itineraire,
            permissions=(
                permission_itineraire_view,
                permission_itineraire_create,
                permission_itineraire_delete,
            )
        )

        from django.db.models.signals import post_save
        from mayan.apps.documents.models.document_file_models import DocumentFile
        from .handlers import handler_parse_gpx

        post_save.connect(
            receiver=handler_parse_gpx,
            sender=DocumentFile,
            dispatch_uid='itineraires_handler_parse_gpx'
        )

        from mayan.apps.common.menus import menu_object, menu_tools
        from mayan.apps.documents.models.document_models import Document
        from .links import link_itineraire_map, link_itineraire_stats

        menu_tools.bind_links(
            links=(link_itineraire_stats,)
        )

        menu_object.bind_links(
            links=(link_itineraire_map,),
            sources=(Document,)
        )

        from . import queues  # noqa

        # Enregistrement des URLs API — protégé par flag de classe
        if not ItinerairesConfig._api_urls_registered:
            from mayan.apps.rest_api.urls import api_version_urls
            from .urls import api_urls as itineraire_api_urls
            api_version_urls.extend(itineraire_api_urls)
            ItinerairesConfig._api_urls_registered = True
            logger.debug('App itineraires — URLs API enregistrées.')

        logger.debug('App itineraires prête.')
