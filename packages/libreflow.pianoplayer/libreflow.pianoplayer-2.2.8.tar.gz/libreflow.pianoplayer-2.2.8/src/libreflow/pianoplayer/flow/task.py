from kabaret import flow
from libreflow.baseflow.task import ManagedTask

from .compositing import InitCompScene, UpdateCompScene


class Task(ManagedTask):
    
    initialise_scene = flow.Child(InitCompScene)
    update_scene     = flow.Child(UpdateCompScene)
