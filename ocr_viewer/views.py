import json
import logging

from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views import View

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view

from .permissions import permission_ocr_viewer_view

logger = logging.getLogger(name=__name__)


class DocumentOCRViewerView(View):
    template_name = 'ocr_viewer/ocr_viewer.html'

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

    def get(self, request, *args, **kwargs):
        document = self.get_document()

        # Liste du contenu OCR par page (une entrée par page)
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
            logger.error(
                'DocumentOCRViewerView — erreur lecture OCR '
                'document %s : %s', document.pk, e
            )

        ocr_content = '\n'.join(ocr_pages)

        return render(request, self.template_name, {
            'document': document,
            'ocr_content': ocr_content,
            'ocr_pages_json': json.dumps(ocr_pages, ensure_ascii=False),
            'title': _('OCR du document : %s') % document.label,
            'object': document,
        })
