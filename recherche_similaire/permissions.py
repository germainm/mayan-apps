from django.utils.translation import gettext_lazy as _

from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_(message='Recherche similaire'),
    name='recherche_similaire'
)

permission_similaire_view = namespace.add_permission(
    label=_(message='Voir les documents similaires'),
    name='similaire_view'
)
