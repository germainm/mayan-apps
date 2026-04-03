from django.urls import re_path
from . import views

urlpatterns = [
    re_path(
        route=r'^$',
        view=views.DocumentHealthDashboardView.as_view(),
        name='dashboard'
    ),
    re_path(
        route=r'^no-mimetype/$',
        view=views.DocumentHealthNoMimetypeView.as_view(),
        name='no_mimetype'
    ),
    re_path(
        route=r'^no-pages/$',
        view=views.DocumentHealthNoPagesView.as_view(),
        name='no_pages'
    ),
    re_path(
        route=r'^no-ocr/$',
        view=views.DocumentHealthNoOCRView.as_view(),
        name='no_ocr'
    ),
]
