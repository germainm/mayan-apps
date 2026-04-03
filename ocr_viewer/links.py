from django.utils.translation import gettext_lazy as _
from mayan.apps.navigation.links import Link
from .icons import icon_ocr_viewer
from .permissions import permission_ocr_viewer_view

link_document_ocr_viewer = Link(
    icon=icon_ocr_viewer,
    permission=permission_ocr_viewer_view,
    text=_(message='OCR du document'),
    view='ocr_viewer:document_ocr_viewer',
    args='resolved_object.pk'
)
