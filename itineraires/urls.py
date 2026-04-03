from django.urls import re_path

from . import api_views, views

# URLs web (HTML)
# Lues par MayanAppConfig.configure_urls() — préfixe /itineraires/
urlpatterns = [
    re_path(
        route=r'^stats/$',
        view=views.ItineraireStatsView.as_view(),
        name='stats'
    ),
    re_path(
        route=r'^carte/(?P<pk>\d+)/$',
        view=views.ItineraireMapView.as_view(),
        name='map'
    ),
]

# URLs API (JSON)
# Lues par rest_api/apps.py — enregistrées sous /api/v4/
api_urls = [
    re_path(
        route=r'^itineraires/$',
        view=api_views.ItineraireListAPIView.as_view(),
        name='itineraire-list'
    ),
    re_path(
        route=r'^itineraires/(?P<pk>\d+)/$',
        view=api_views.ItineraireDetailAPIView.as_view(),
        name='itineraire-detail'
    ),
    re_path(
        route=r'^itineraires/(?P<pk>\d+)/gpx/$',
        view=api_views.ItineraireGPXAPIView.as_view(),
        name='itineraire-gpx'
    ),
    re_path(
        route=r'^itineraires/stats/jour/$',
        view=api_views.ItineraireStatsJourAPIView.as_view(),
        name='itineraire-stats-jour'
    ),
    re_path(
        route=r'^itineraires/stats/semaine/$',
        view=api_views.ItineraireStatsSemaineAPIView.as_view(),
        name='itineraire-stats-semaine'
    ),
    re_path(
        route=r'^itineraires/stats/mois/$',
        view=api_views.ItineraireStatsMoisAPIView.as_view(),
        name='itineraire-stats-mois'
    ),
]
