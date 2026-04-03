from django.utils.translation import gettext_lazy as _
from mayan.apps.task_manager.classes import CeleryQueue, Worker, Task

queue_itineraires = CeleryQueue(
    label=_(message='Itinéraires'),
    name='itineraires',
    worker=Worker(name='worker_b')
)

queue_itineraires.add_task_type(
    dotted_path='mayan.apps.itineraires.tasks.task_parse_gpx',
    label=_(message='Analyser un fichier GPX')
)
