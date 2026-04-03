# FICHIER : mayan/apps/recherche_similaire/views.py  (version corrigée complète)

import logging

from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.translation import gettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.views.generics import SingleObjectListView

from .permissions import permission_similaire_view

logger = logging.getLogger(name=__name__)

SIMILAIRES_COUNT = 10
SCORE_MINIMUM = 0.1

# Seuil absolu de score ES — en dessous, on considère que les résultats
# ne sont pas pertinents même relativement (Fix 🟡 : score relatif trompeur)
SCORE_MAX_MINIMUM_ABSOLU = 2.0

INDEX_DOCUMENTS = 'mayan--documents.documentsearchresult'
CHAMPS_CONTENU = [
    'versions__version_pages__ocr_content__content',
    'files__file_pages__content__content',
]

# Fix 4 : timeout Elasticsearch en secondes
# Évite de bloquer un worker Gunicorn sur une requête more_like_this lente.
ES_REQUEST_TIMEOUT = 10


def get_elasticsearch_client():
    from mayan.apps.dynamic_search.search_backends import SearchBackend
    backend = SearchBackend.get_instance()
    return backend._client


class DocumentSimilairesView(SingleObjectListView):
    template_name = 'recherche_similaire/similaires.html'
    object_permission = permission_similaire_view

    def get_document(self):
        if not hasattr(self, '_document'):
            self._document = get_object_or_404(
                AccessControlList.objects.restrict_queryset(
                    permission=permission_document_view,
                    queryset=Document.valid.all(),
                    user=self.request.user
                ),
                pk=self.kwargs['document_id']
            )
        return self._document

    def get_similaires_depuis_elasticsearch(self):
        document = self.get_document()

        try:
            client = get_elasticsearch_client()
        except Exception as e:
            logger.error(
                'DocumentSimilairesView — impossible de se connecter '
                'a Elasticsearch : %s', e
            )
            return []

        try:
            reponse = client.search(
                index=INDEX_DOCUMENTS,
                body={
                    'size': SIMILAIRES_COUNT + 1,
                    'query': {
                        'more_like_this': {
                            'fields': CHAMPS_CONTENU,
                            'like': [
                                {
                                    '_index': INDEX_DOCUMENTS,
                                    '_id': str(document.pk)
                                }
                            ],
                            'min_term_freq': 1,
                            'max_query_terms': 25,
                            'min_doc_freq': 1,
                            'minimum_should_match': '30%'
                        }
                    },
                    '_source': False
                },
                # Fix 4 : timeout explicite — évite de bloquer le worker gevent
                request_timeout=ES_REQUEST_TIMEOUT
            )
        except Exception as e:
            logger.error(
                'DocumentSimilairesView — erreur requete Elasticsearch '
                'pour document %s : %s', document.pk, e
            )
            return []

        hits = reponse.get('hits', {}).get('hits', [])

        if not hits:
            return []

        score_max = hits[0]['_score'] if hits else 0
        if score_max == 0:
            return []

        # Fix 🟡 : seuil absolu — si le meilleur score ES est trop faible,
        # les résultats ne sont pas pertinents même à 100% relatif
        if score_max < SCORE_MAX_MINIMUM_ABSOLU:
            logger.debug(
                'DocumentSimilairesView — score_max trop faible (%.2f < %.2f) '
                'pour document %s, aucun résultat retourné',
                score_max, SCORE_MAX_MINIMUM_ABSOLU, document.pk
            )
            return []

        resultats = []
        for hit in hits:
            doc_id = int(hit['_id'])

            if doc_id == document.pk:
                continue

            score_normalise = hit['_score'] / score_max
            if score_normalise < SCORE_MINIMUM:
                continue

            resultats.append({
                'document_id': doc_id,
                'score_pct': int(score_normalise * 100),
            })

        return resultats[:SIMILAIRES_COUNT]

    def get_source_queryset(self):
        similaires = self.get_similaires_depuis_elasticsearch()

        if not similaires:
            return Document.objects.none()

        ids_similaires = [s['document_id'] for s in similaires]

        docs_visibles = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.valid.filter(pk__in=ids_similaires),
            user=self.request.user
        )

        scores_par_id = {s['document_id']: s['score_pct'] for s in similaires}

        docs_avec_scores = []
        for doc in docs_visibles:
            doc.score_similarite = scores_par_id.get(doc.pk, 0)
            docs_avec_scores.append(doc)

        docs_avec_scores.sort(
            key=lambda d: d.score_similarite,
            reverse=True
        )

        return docs_avec_scores

    def get_extra_context(self):
        document = self.get_document()
        return {
            'title': _(
                message='Documents similaires a : %s'
            ) % document.label,
            'document': document,
            'hide_object': True,
            'no_results_text': _(
                message='Aucun document similaire trouve. '
                'Ce document n a peut-etre pas encore ete traite '
                'par l OCR, ou aucun autre document ne partage '
                'de contenu similaire.'
            ),
            'no_results_title': _(
                message='Pas de documents similaires'
            ),
        }

    def get(self, request, *args, **kwargs):
        self.get_document()
        return super().get(request, *args, **kwargs)


class DocumentSimilairesAPIView(View):
    """Vue API REST — retourne les documents similaires en JSON."""

    def get(self, request, document_id):
        from django.http import JsonResponse
        from mayan.apps.acls.models import AccessControlList
        from mayan.apps.documents.models.document_models import Document
        from mayan.apps.documents.permissions import permission_document_view

        try:
            document = get_object_or_404(
                AccessControlList.objects.restrict_queryset(
                    permission=permission_document_view,
                    queryset=Document.valid.all(),
                    user=request.user
                ),
                pk=document_id
            )
        except Exception:
            return JsonResponse({'error': 'Document non trouvé'}, status=404)

        # Réutiliser la logique existante
        view = DocumentSimilairesView()
        view.kwargs = {'document_id': document_id}
        view.request = request
        view._document = document

        similaires = view.get_similaires_depuis_elasticsearch()

        if not similaires:
            return JsonResponse({'results': []})

        ids = [s['document_id'] for s in similaires]
        scores = {s['document_id']: s['score_pct'] for s in similaires}

        docs = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.valid.filter(pk__in=ids),
            user=request.user
        )

        results = []
        for doc in docs:
            results.append({
                'id': doc.pk,
                'label': doc.label,
                'score_pct': scores.get(doc.pk, 0),
                'document_type': {'label': doc.document_type.label if doc.document_type else ''},
                'datetime_created': doc.datetime_created.isoformat(),
            })

        results.sort(key=lambda x: x['score_pct'], reverse=True)

        return JsonResponse({'results': results})
