from django.utils.translation import gettext_lazy as _
from mayan.apps.navigation.links import Link
from .icons import (
    icon_document_health,
    icon_health_no_mimetype,
    icon_health_no_pages,
    icon_health_no_ocr,
)
from .permissions import permission_document_health_view

link_document_health = Link(
    icon=icon_document_health,
    permission=permission_document_health_view,
    text=_(message='Qualité des documents'),
    view='document_health:dashboard',
)
link_health_no_mimetype = Link(
    icon=icon_health_no_mimetype,
    permission=permission_document_health_view,
    text=_(message='Sans type MIME'),
    view='document_health:no_mimetype',
)
link_health_no_pages = Link(
    icon=icon_health_no_pages,
    permission=permission_document_health_view,
    text=_(message='Sans pages'),
    view='document_health:no_pages',
)
link_health_no_ocr = Link(
    icon=icon_health_no_ocr,
    permission=permission_document_health_view,
    text=_(message='Sans OCR'),
    view='document_health:no_ocr',
)
