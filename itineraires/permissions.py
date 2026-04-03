from django.utils.translation import gettext_lazy as _

from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_(message='Itinéraires'),
    name='itineraires'
)

permission_itineraire_view = namespace.add_permission(
    label=_(message='Voir les statistiques de trajets'),
    name='itineraire_view'
)

permission_itineraire_create = namespace.add_permission(
    label=_(message='Créer un itinéraire'),
    name='itineraire_create'
)

permission_itineraire_delete = namespace.add_permission(
    label=_(message='Supprimer un itinéraire'),
    name='itineraire_delete'
)
