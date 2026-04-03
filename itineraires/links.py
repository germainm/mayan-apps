# FICHIER : mayan/apps/itineraires/links.py  (correction signature condition)

from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.links import Link

from .icons import icon_itineraire_map, icon_itineraire_stats
from .permissions import permission_itineraire_view


def _document_a_itineraire(context, resolved_object):
    """
    Condition pour le lien 'Voir la carte'.
    Mayan passe resolved_object comme kwarg nommé — pas via context.
    """
    if resolved_object is None:
        return False
    try:
        return resolved_object.itineraire.gpx_parsed
    except Exception:
        return False


link_itineraire_stats = Link(
    icon=icon_itineraire_stats,
    permission=permission_itineraire_view,
    text=_(message='Statistiques trajets'),
    view='itineraires:stats'
)

link_itineraire_map = Link(
    condition=_document_a_itineraire,
    icon=icon_itineraire_map,
    permission=permission_itineraire_view,
    text=_(message='Voir la carte'),
    view='itineraires:map',
    args='resolved_object.itineraire.pk'
)
