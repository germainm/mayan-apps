# FICHIER : mayan/apps/itineraires/api_views.py  (version corrigée complète)

import logging
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.rest_api.generics import ListAPIView, RetrieveAPIView

from .gpx_utils import parse_gpx_safe  # Fix 2
from .models import Itineraire
from .permissions import permission_itineraire_view
from .serializers import ItineraireSerializer, ItineraireGPXSerializer

logger = logging.getLogger(name=__name__)

# Longueur maximale du filtre conducteur (aligné sur le modèle)
CONDUCTEUR_MAX_LEN = 255

# TTL du cache GPX en secondes (1 heure)
# Le cache est invalidé automatiquement si l'itineraire est modifié
# (voir signal post_save dans handlers.py si tu veux l'invalider activement)
GPX_CACHE_TTL = 3600


def _get_conducteur_param(request):
    """
    Lit et valide le paramètre ?conducteur= de la requête.
    Retourne une string tronquée ou None.
    """
    conducteur = request.query_params.get('conducteur')
    if not conducteur:
        return None
    # Tronquer silencieusement — pas d'erreur 400, juste une protection
    return conducteur[:CONDUCTEUR_MAX_LEN]


class ItineraireQuerysetMixin:
    """
    Mixin réutilisable — filtre par ACL document + conducteur optionnel.
    """
    def get_itineraire_queryset(self):
        docs_visibles = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.valid.all(),
            user=self.request.user
        )
        qs = Itineraire.objects.filter(
            document__in=docs_visibles,
            gpx_parsed=True
        ).select_related('document')

        # Fix 3 : validation de longueur sur le paramètre conducteur
        conducteur = _get_conducteur_param(self.request)
        if conducteur:
            qs = qs.filter(conducteur=conducteur)

        return qs


class ItineraireListAPIView(ItineraireQuerysetMixin, ListAPIView):
    serializer_class = ItineraireSerializer
    mayan_object_permissions = {'GET': (permission_itineraire_view,)}

    def get_source_queryset(self):
        return self.get_itineraire_queryset().order_by('-date_trajet')


class ItineraireDetailAPIView(ItineraireQuerysetMixin, RetrieveAPIView):
    serializer_class = ItineraireSerializer
    mayan_object_permissions = {'GET': (permission_itineraire_view,)}

    def get_source_queryset(self):
        return self.get_itineraire_queryset()


class ItineraireStatsJourAPIView(ItineraireQuerysetMixin, ListAPIView):
    serializer_class = ItineraireSerializer
    mayan_object_permissions = {'GET': (permission_itineraire_view,)}

    def get_source_queryset(self):
        depuis = timezone.now().date() - timedelta(days=30)
        return (
            self.get_itineraire_queryset()
            .filter(date_trajet__gte=depuis)
            .annotate(periode=TruncDay('date_trajet'))
            .values('periode')
            .annotate(total_km=Sum('distance_km'))
            .order_by('periode')
        )

    def list(self, request, *args, **kwargs):
        from rest_framework.response import Response
        data = [
            {
                'date': item['periode'].strftime('%Y-%m-%d'),
                'total_km': float(item['total_km'])
            }
            for item in self.get_queryset()
        ]
        return Response(data=data)


class ItineraireStatsSemaineAPIView(ItineraireQuerysetMixin, ListAPIView):
    serializer_class = ItineraireSerializer
    mayan_object_permissions = {'GET': (permission_itineraire_view,)}

    def get_source_queryset(self):
        depuis = timezone.now().date() - timedelta(weeks=12)
        return (
            self.get_itineraire_queryset()
            .filter(date_trajet__gte=depuis)
            .annotate(periode=TruncWeek('date_trajet'))
            .values('periode')
            .annotate(total_km=Sum('distance_km'))
            .order_by('periode')
        )

    def list(self, request, *args, **kwargs):
        from rest_framework.response import Response
        data = [
            {
                'semaine': '{}-W{}'.format(
                    item['periode'].year,
                    item['periode'].strftime('%W')
                ),
                'total_km': float(item['total_km'])
            }
            for item in self.get_queryset()
        ]
        return Response(data=data)


class ItineraireStatsMoisAPIView(ItineraireQuerysetMixin, ListAPIView):
    serializer_class = ItineraireSerializer
    mayan_object_permissions = {'GET': (permission_itineraire_view,)}

    def get_source_queryset(self):
        depuis = timezone.now().date() - timedelta(days=365)
        return (
            self.get_itineraire_queryset()
            .filter(date_trajet__gte=depuis)
            .annotate(periode=TruncMonth('date_trajet'))
            .values('periode')
            .annotate(total_km=Sum('distance_km'))
            .order_by('periode')
        )

    def list(self, request, *args, **kwargs):
        from rest_framework.response import Response
        data = [
            {
                'mois': item['periode'].strftime('%Y-%m'),
                'total_km': float(item['total_km'])
            }
            for item in self.get_queryset()
        ]
        return Response(data=data)


class ItineraireGPXAPIView(ItineraireQuerysetMixin, RetrieveAPIView):
    """
    GET /api/v4/itineraires/{pk}/gpx/

    Fix 3 : les points GPX sont mis en cache Redis (TTL 1h).
    Fix 2 : lecture bornée via parse_gpx_safe().
    """
    serializer_class = ItineraireGPXSerializer
    mayan_object_permissions = {'GET': (permission_itineraire_view,)}

    def get_source_queryset(self):
        return self.get_itineraire_queryset()

    def retrieve(self, request, *args, **kwargs):
        from rest_framework.response import Response

        itineraire = self.get_object()

        # Clé de cache par itinéraire — invalider si le fichier GPX change
        cache_key = 'itineraire_gpx_points_{}'.format(itineraire.pk)
        cached = cache.get(cache_key)

        if cached is not None:
            return Response(data=cached)

        try:
            doc_file = itineraire.document.file_latest
            # Fix 2 : taille vérifiée avant parsing
            gpx = parse_gpx_safe(doc_file)
        except ValueError as e:
            # Fichier trop volumineux
            return Response(
                data={'error': str(e)},
                status=400
            )
        except Exception as e:
            logger.error(
                'ItineraireGPXAPIView — erreur lecture GPX '
                'pour itineraire %s : %s', itineraire.pk, e
            )
            return Response(
                data={'error': 'Fichier GPX inaccessible'},
                status=500
            )

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append([point.latitude, point.longitude])

        if not points:
            return Response(
                data={'error': 'Aucun point GPS dans ce fichier'},
                status=404
            )

        lats = [p[0] for p in points]
        lons = [p[1] for p in points]
        centre = [sum(lats) / len(lats), sum(lons) / len(lons)]

        payload = {
            'points': points,
            'centre': centre,
            'distance_km': float(itineraire.distance_km),
            'nb_points': len(points),
        }

        # Mise en cache Redis — la prochaine requête ne re-parse pas le fichier
        cache.set(cache_key, payload, timeout=GPX_CACHE_TTL)

        return Response(data=payload)
