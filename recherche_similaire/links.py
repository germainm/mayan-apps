from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.links import Link

from .icons import icon_similaire
from .permissions import permission_similaire_view


link_document_similaires = Link(
    icon=icon_similaire,
    permission=permission_similaire_view,
    text=_(message='Documents similaires'),
    view='recherche_similaire:document_similaires',
    args='resolved_object.pk'
)
