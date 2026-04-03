from django.utils.translation import gettext_lazy as _
from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_(message='Qualité des documents'),
    name='document_health'
)

permission_document_health_view = namespace.add_permission(
    label=_(message='Voir le rapport de qualité des documents'),
    name='document_health_view'
)
