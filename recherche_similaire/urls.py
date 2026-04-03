from django.urls import re_path

from . import views

# URLs web (HTML)
# Lues par MayanAppConfig.configure_urls()
# sous le préfixe /recherche_similaire/
urlpatterns = [
    re_path(
        route=r'^documents/(?P<document_id>\d+)/similaires/$',
        view=views.DocumentSimilairesView.as_view(),
        name='document_similaires'
    ),
]

from django.urls import re_path
from . import views

urlpatterns += [
    re_path(
        route=r'^documents/(?P<document_id>\d+)/similaires/api/$',
        view=views.DocumentSimilairesAPIView.as_view(),
        name='document_similaires_api'
    ),
]

# URLs API REST
from .api_views import DocumentSimilairesAPIView
from django.urls import re_path as api_re_path

api_urls = [
    api_re_path(
        route=r'^documents/(?P<document_id>\d+)/similaires/$',
        view=DocumentSimilairesAPIView.as_view(),
        name='document_similaires_api'
    ),
]
