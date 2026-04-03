from django.db import models
from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.models.document_models import Document


class Itineraire(models.Model):
    document = models.OneToOneField(
        on_delete=models.CASCADE,
        related_name='itineraire',
        to=Document,
        verbose_name=_(message='Document')
    )
    conducteur = models.CharField(
        db_index=True,
        max_length=255,
        verbose_name=_(message='Conducteur')
    )
    date_trajet = models.DateField(
        db_index=True,
        verbose_name=_(message='Date du trajet')
    )
    distance_km = models.DecimalField(
        decimal_places=3,
        max_digits=8,
        verbose_name=_(message='Distance (km)')
    )
    duree_secondes = models.PositiveIntegerField(
        default=0,
        verbose_name=_(message='Durée (secondes)')
    )
    gpx_parsed = models.BooleanField(
        default=False,
        verbose_name=_(message='GPX parsé')
    )

    class Meta:
        ordering = ['-date_trajet']
        verbose_name = _(message='Itinéraire')
        verbose_name_plural = _(message='Itinéraires')

    def __str__(self):
        return '{} — {} — {} km'.format(
            self.conducteur, self.date_trajet, self.distance_km
        )

    @property
    def duree_formatee(self):
        heures = self.duree_secondes // 3600
        minutes = (self.duree_secondes % 3600) // 60
        return '{}h{:02d}'.format(heures, minutes)
