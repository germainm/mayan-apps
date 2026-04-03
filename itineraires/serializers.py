from mayan.apps.rest_api import serializers

from .models import Itineraire


class ItineraireSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Itineraire
        fields = (
            'id', 'conducteur', 'date_trajet',
            'distance_km', 'duree_secondes', 'gpx_parsed',
        )
        read_only_fields = (
            'id', 'distance_km', 'duree_secondes', 'gpx_parsed',
        )


class ItineraireStatsSerializer(serializers.Serializer):
    """
    Serializer pour les données agrégées —
    utilisé pour la documentation auto DRF/Swagger.
    """
    total_km = serializers.DecimalField(
        max_digits=10, decimal_places=3, read_only=True
    )


class ItineraireGPXSerializer(serializers.Serializer):
    """
    Serializer pour la réponse GPX —
    utilisé pour la documentation auto DRF/Swagger.
    """
    points = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField()
        ),
        read_only=True
    )
    centre = serializers.ListField(
        child=serializers.FloatField(),
        read_only=True
    )
    distance_km = serializers.FloatField(read_only=True)
    nb_points = serializers.IntegerField(read_only=True)
