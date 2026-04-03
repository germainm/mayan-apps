import logging

from django.db.models import Count, Q
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.views.generics import SingleObjectListView

from .permissions import permission_document_health_view

logger = logging.getLogger(name=__name__)


def get_valid_documents(user):
    """Retourne les documents valides visibles par l'utilisateur."""
    return AccessControlList.objects.restrict_queryset(
        permission=permission_document_view,
        queryset=Document.valid.all(),
        user=user
    )


class DocumentHealthDashboardView(View):
    """Vue tableau de bord — compteurs des trois catégories de problèmes."""
    template_name = 'document_health/dashboard.html'

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm('document_health.document_health_view'):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

        qs = get_valid_documents(request.user)

        # Documents sans mimetype
        count_no_mimetype = qs.filter(
            Q(files__mimetype__isnull=True) | Q(files__mimetype='')
        ).distinct().count()

        # Documents sans pages (version active sans pages)
        count_no_pages = qs.filter(
            version_active__isnull=False
        ).annotate(
            page_count=Count('version_active__version_pages')
        ).filter(page_count=0).count()

        # Documents sans OCR (version active avec pages mais sans contenu OCR)
        from mayan.apps.ocr.models import DocumentVersionPageOCRContent
        docs_with_ocr = DocumentVersionPageOCRContent.objects.filter(
            content__isnull=False
        ).exclude(content='').values_list(
            'document_version_page__document_version__document_id',
            flat=True
        ).distinct()

        count_no_ocr = qs.filter(
            version_active__isnull=False
        ).annotate(
            page_count=Count('version_active__version_pages')
        ).filter(
            page_count__gt=0
        ).exclude(pk__in=docs_with_ocr).count()

        total_docs = qs.count()

        return render(request, self.template_name, {
            'title': _('Qualité des documents'),
            'total_docs': total_docs,
            'count_no_mimetype': count_no_mimetype,
            'count_no_pages': count_no_pages,
            'count_no_ocr': count_no_ocr,
        })


class DocumentHealthNoMimetypeView(SingleObjectListView):
    """Documents sans type MIME détecté."""
    object_permission = permission_document_view
    view_icon = None

    def get_source_queryset(self):
        return get_valid_documents(self.request.user).filter(
            Q(files__mimetype__isnull=True) | Q(files__mimetype='')
        ).distinct().order_by('label')

    def get_extra_context(self):
        return {
            'title': _('Documents sans type MIME (%d)') % self.get_source_queryset().count(),
            'no_results_title': _('Aucun document sans type MIME'),
            'no_results_text': _('Tous les documents ont un type MIME détecté.'),
            'hide_object': True,
        }


class DocumentHealthNoPagesView(SingleObjectListView):
    """Documents avec 0 pages."""
    object_permission = permission_document_view
    view_icon = None

    def get_source_queryset(self):
        return get_valid_documents(self.request.user).filter(
            version_active__isnull=False
        ).annotate(
            page_count=Count('version_active__version_pages')
        ).filter(page_count=0).order_by('label')

    def get_extra_context(self):
        return {
            'title': _('Documents sans pages (%d)') % self.get_source_queryset().count(),
            'no_results_title': _('Aucun document sans pages'),
            'no_results_text': _('Tous les documents ont au moins une page.'),
            'hide_object': True,
        }


class DocumentHealthNoOCRView(SingleObjectListView):
    """Documents avec pages mais sans contenu OCR."""
    object_permission = permission_document_view
    view_icon = None

    def get_source_queryset(self):
        from mayan.apps.ocr.models import DocumentVersionPageOCRContent
        docs_with_ocr = DocumentVersionPageOCRContent.objects.filter(
            content__isnull=False
        ).exclude(content='').values_list(
            'document_version_page__document_version__document_id',
            flat=True
        ).distinct()

        return get_valid_documents(self.request.user).filter(
            version_active__isnull=False
        ).annotate(
            page_count=Count('version_active__version_pages')
        ).filter(
            page_count__gt=0
        ).exclude(pk__in=docs_with_ocr).order_by('label')

    def get_extra_context(self):
        return {
            'title': _('Documents sans OCR (%d)') % self.get_source_queryset().count(),
            'no_results_title': _('Aucun document sans OCR'),
            'no_results_text': _('Tous les documents ont un contenu OCR.'),
            'hide_object': True,
        }
