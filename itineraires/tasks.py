# FICHIER : mayan/apps/itineraires/tasks.py

import logging

from mayan.celery import app
from mayan.apps.documents.models.document_file_models import DocumentFile

from .gpx_utils import parse_gpx_safe
from .models import Itineraire

logger = logging.getLogger(name=__name__)


@app.task(
    ignore_result=True,
    queue='itineraires'       # ← lié à la bonne queue
)
def task_parse_gpx(document_file_id):
    logger.info(
        'task_parse_gpx — début pour DocumentFile id=%s', document_file_id
    )

    try:
        doc_file = DocumentFile.objects.get(pk=document_file_id)
    except DocumentFile.DoesNotExist:
        logger.warning(
            'task_parse_gpx — DocumentFile %s introuvable', document_file_id
        )
        return

    logger.info(
        'task_parse_gpx — taille fichier : %.1f Mo pour DocumentFile %s',
        doc_file.size / 1024 / 1024,
        document_file_id
    )

    try:
        gpx = parse_gpx_safe(doc_file)
    except ValueError as e:
        logger.warning(
            'task_parse_gpx — fichier rejeté pour DocumentFile %s : %s',
            document_file_id, e
        )
        return
    except Exception as e:
        logger.error(
            'task_parse_gpx — erreur parsing GPX pour DocumentFile %s : %s',
            document_file_id, e
        )
        return

    distance_km = (gpx.length_3d() or gpx.length_2d() or 0) / 1000

    try:
        date_trajet = gpx.tracks[0].segments[0].points[0].time.date()
    except (IndexError, AttributeError):
        from django.utils import timezone
        date_trajet = timezone.now().date()
        logger.warning(
            'task_parse_gpx — pas de timestamp dans le GPX, '
            'utilisation de la date du jour'
        )

    duree_secondes = 0
    moving_data = gpx.get_moving_data()
    if moving_data:
        duree_secondes = int(moving_data.moving_time)

    conducteur = ''
    try:
        conducteur = doc_file.document.metadata.filter(
            metadata_type__name='Conducteur'
        ).values_list('value', flat=True).first() or ''
    except Exception as e:
        logger.warning(
            'task_parse_gpx — impossible de lire la métadonnée conducteur '
            'pour DocumentFile %s : %s', document_file_id, e
        )

    Itineraire.objects.update_or_create(
        document=doc_file.document,
        defaults={
            'conducteur': conducteur,
            'date_trajet': date_trajet,
            'distance_km': distance_km,
            'duree_secondes': duree_secondes,
            'gpx_parsed': True,
        }
    )

    try:
        from django.core.cache import cache
        itineraire = Itineraire.objects.get(document=doc_file.document)
        cache.delete('itineraire_gpx_points_{}'.format(itineraire.pk))
    except Exception:
        pass

    logger.info(
        'task_parse_gpx — terminé : conducteur=%s, date=%s, distance=%.3f km',
        conducteur, date_trajet, distance_km
    )
