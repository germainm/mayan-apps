# Mayan EDMS — Applications personnalisées

Applications Django custom développées pour Mayan EDMS 4.11 (Django 5.2, Python 3.13).

## Applications incluses

### ocr_viewer
Panneau OCR avec recherche et surlignage. Affiche le contenu OCR de chaque page d'un document avec navigation et mise en évidence des termes recherchés.

### recherche_similaire
Recherche de documents similaires via Elasticsearch `more_like_this`. Retourne les documents les plus proches du document courant avec un score de similarité.

### document_health
Tableau de bord de qualité documentaire. Affiche des métriques sur l'état des documents (OCR manquant, métadonnées incomplètes, etc.).

### itineraires
Suivi de trajets GPX pour conducteurs. Affiche des cartes Leaflet avec statistiques de distance pour les itinéraires en Bas-Saint-Laurent.

## Installation

Copier les dossiers dans votre installation Mayan :
```bash
cp -r ocr_viewer /opt/mayan-edms/lib/pythonX.XX/site-packages/mayan/apps/
cp -r recherche_similaire /opt/mayan-edms/lib/pythonX.XX/site-packages/mayan/apps/
cp -r document_health /opt/mayan-edms/lib/pythonX.XX/site-packages/mayan/apps/
cp -r itineraires /opt/mayan-edms/lib/pythonX.XX/site-packages/mayan/apps/
```

Ajouter dans `config.yml` :
```yaml
COMMON_EXTRA_APPS:
  - mayan.apps.ocr_viewer.apps.OCRViewerConfig
  - mayan.apps.recherche_similaire.apps.RechercheSimilaireConfig
  - mayan.apps.document_health.apps.DocumentHealthConfig
  - mayan.apps.itineraires.apps.ItinerairesConfig
```

## Auteur

Germain — [MyPalace](https://www.mypalace.ca)

Développement sur mesure d'applications Mayan EDMS et interfaces mobiles PWA.
