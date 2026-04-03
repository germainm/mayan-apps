import logging
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view

logger = logging.getLogger(name=__name__)


class DocumentOCRAPIView(APIView):

    def get(self, request, document_id):
        document = get_object_or_404(
            AccessControlList.objects.restrict_queryset(
                permission=permission_document_view,
                queryset=Document.valid.all(),
                user=request.user
            ),
            pk=document_id
        )

        ocr_pages = []
        try:
            version = document.version_active
            if version:
                for page in version.pages.order_by('page_number'):
                    try:
                        ocr_pages.append(page.ocr_content.content or '')
                    except Exception:
                        ocr_pages.append('')
        except Exception as e:
            logger.error('DocumentOCRAPIView error: %s', e)

        return Response({
            'document_id': document.pk,
            'pages': ocr_pages,
            'content': '\n'.join(ocr_pages)
        })
