from django.utils.translation import gettext_lazy as _
from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_(message='OCR Viewer'),
    name='ocr_viewer'
)

permission_ocr_viewer_view = namespace.add_permission(
    label=_(message='Voir le contenu OCR du document'),
    name='ocr_viewer_view'
)
