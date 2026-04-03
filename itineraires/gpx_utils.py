# FICHIER : mayan/apps/itineraires/gpx_utils.py  (nouveau fichier utilitaire)
#
# Centralise la lecture sécurisée d'un fichier GPX avec limite de taille.
# Utilisé par tasks.py ET api_views.py pour éviter la duplication.

import logging

import gpxpy

logger = logging.getLogger(name=__name__)

# Taille maximale d'un fichier GPX accepté (10 Mo)
# Un enregistrement GPX de 24h à 1 point/seconde fait ~15 Mo en XML brut.
# 10 Mo couvre ~16h d'enregistrement continu — ajuster si besoin.
GPX_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 Mo


def parse_gpx_safe(doc_file):
    """
    Ouvre et parse un DocumentFile GPX de manière sécurisée.

    - Vérifie la taille avant de lire le contenu
    - Lève ValueError si trop grand
    - Lève toute exception gpxpy en cas de fichier invalide

    Retourne un objet gpxpy.GPX.
    """
    # Vérification de taille via les métadonnées du fichier Mayan
    # DocumentFile expose .size (en octets) sans ouvrir le fichier
    try:
        file_size = doc_file.size
    except AttributeError:
        # Fallback si l'attribut n'existe pas (version Mayan différente)
        file_size = None

    if file_size is not None and file_size > GPX_MAX_SIZE_BYTES:
        raise ValueError(
            'Fichier GPX trop volumineux ({} Mo > {} Mo max)'.format(
                round(file_size / 1024 / 1024, 1),
                GPX_MAX_SIZE_BYTES // 1024 // 1024
            )
        )

    with doc_file.open() as f:
        # Lecture bornée — protection supplémentaire si .size n'est pas fiable
        content = f.read(GPX_MAX_SIZE_BYTES + 1)

    if len(content) > GPX_MAX_SIZE_BYTES:
        raise ValueError(
            'Fichier GPX trop volumineux (> {} Mo)'.format(
                GPX_MAX_SIZE_BYTES // 1024 // 1024
            )
        )

    # gpxpy.parse() accepte une string ou bytes
    import io
    return gpxpy.parse(io.BytesIO(content) if isinstance(content, bytes) else io.StringIO(content))


# ===========================================================================
# MODIFICATIONS À APPORTER dans tasks.py
# ===========================================================================
#
# AVANT :
#   with doc_file.open() as f:
#       gpx = gpxpy.parse(f)
#
# APRÈS :
#   from .gpx_utils import parse_gpx_safe
#   try:
#       gpx = parse_gpx_safe(doc_file)
#   except ValueError as e:
#       logger.warning(
#           'task_parse_gpx — fichier rejeté pour DocumentFile %s : %s',
#           document_file_id, e
#       )
#       return
#   except Exception as e:
#       logger.error(
#           'task_parse_gpx — erreur parsing GPX pour DocumentFile %s : %s',
#           document_file_id, e
#       )
#       return


# ===========================================================================
# MODIFICATIONS À APPORTER dans api_views.py — ItineraireGPXAPIView.retrieve()
# ===========================================================================
#
# AVANT :
#   doc_file = itineraire.document.file_latest
#   with doc_file.open() as f:
#       gpx = gpxpy.parse(f)
#
# APRÈS :
#   from .gpx_utils import parse_gpx_safe
#   doc_file = itineraire.document.file_latest
#   try:
#       gpx = parse_gpx_safe(doc_file)
#   except ValueError as e:
#       return Response(
#           data={'error': str(e)},
#           status=400   # Bad Request — fichier trop grand
#       )
#   except Exception as e:
#       logger.error(...)
#       return Response(
#           data={'error': 'Fichier GPX inaccessible'},
#           status=500
#       )
