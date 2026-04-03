import logging

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.views.generics import SingleObjectDetailView, SingleObjectListView

from .models import Itineraire
from .permissions import permission_itineraire_view

logger = logging.getLogger(name=__name__)


class ItineraireStatsView(SingleObjectListView):
    """
    Page principale — graphiques Chart.js.
    Le JS dans le template appelle les api_views pour les données.
    """
    template_name = 'itineraires/stats.html'
    view_permission = permission_itineraire_view

    def get_source_queryset(self):
        docs_visibles = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.valid.all(),
            user=self.request.user
        )
        return Itineraire.objects.filter(
            document__in=docs_visibles,
            gpx_parsed=True
        ).select_related('document')

    def get_extra_context(self):
        qs = self.get_source_queryset()

        conducteurs = (
            qs.values_list('conducteur', flat=True)
            .distinct()
            .order_by('conducteur')
        )

        return {
            'title': 'Statistiques de trajets',
            'conducteurs': conducteurs,
            'conducteur_selectionne': self.request.GET.get('conducteur', ''),
        }


class ItineraireMapView(SingleObjectDetailView):
    """
    Page carte Leaflet pour un trajet spécifique.
    Le JS appelle /api/v4/itineraires/{pk}/gpx/ pour le tracé.
    """
    template_name = 'itineraires/map.html'
    object_permission = permission_itineraire_view
    pk_url_kwarg = 'pk'

    def get_source_queryset(self):
        docs_visibles = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.valid.all(),
            user=self.request.user
        )
        return Itineraire.objects.filter(
            document__in=docs_visibles,
            gpx_parsed=True
        ).select_related('document')

    def get_extra_context(self):
        return {
            'title': 'Carte du trajet — {}'.format(self.object.conducteur),
            'itineraire': self.object,
        }
