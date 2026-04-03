from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view

from .views import DocumentSimilairesView


class DocumentSimilairesAPIView(APIView):

    def get(self, request, document_id):
        document = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.valid.all(),
            user=request.user
        ).filter(pk=document_id).first()

        if not document:
            return Response({'results': []})

        view = DocumentSimilairesView()
        view.kwargs = {'document_id': document_id}
        view.request = request
        view._document = document

        similaires = view.get_similaires_depuis_elasticsearch()

        if not similaires:
            return Response({'results': []})

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

        return Response({'results': results})
