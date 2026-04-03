# FICHIER : mayan/apps/itineraires/handlers.py

import logging

logger = logging.getLogger(name=__name__)


def handler_parse_gpx(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        document_type_label = instance.document.document_type.label
    except Exception as e:
        logger.warning(
            'handler_parse_gpx — impossible de lire le type de document '
            'pour DocumentFile %s : %s', instance.pk, e
        )
        return

    if document_type_label != 'Itinéraire':
        return

    logger.info(
        'handler_parse_gpx — DocumentFile %s détecté comme itinéraire, '
        'lancement du parsing GPX', instance.pk
    )

    from .tasks import task_parse_gpx
    task_parse_gpx.apply_async(
        kwargs={'document_file_id': instance.pk},
        countdown=5,
        queue='itineraires'    # ← manquait
    )
