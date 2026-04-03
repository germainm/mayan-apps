from mayan.apps.dependencies.classes import PythonDependency
from mayan.apps.dependencies.environments import environment_production

PythonDependency(
    environments=(environment_production,),
    module=__name__,
    name='gpxpy',
    version_string='==1.6.2'
)
