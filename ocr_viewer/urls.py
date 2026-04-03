from django.urls import re_path
from . import views
from .api_views import DocumentOCRAPIView

urlpatterns = [
    re_path(
        route=r'^documents/(?P<document_id>\d+)/ocr/$',
        view=views.DocumentOCRViewerView.as_view(),
        name='document_ocr_viewer'
    ),
]

api_urls = [
    re_path(
        route=r'^documents/(?P<document_id>\d+)/ocr/full/$',
        view=DocumentOCRAPIView.as_view(),
        name='document_ocr_api'
    ),
]
