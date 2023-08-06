import logging
from types import SimpleNamespace
from laboro.logger import LaboroLogger

logging.setLoggerClass(LaboroLogger)
logger = logging.getLogger("laboro.main")


class Store:
  """The ``laboro.context.store.Store`` object purpose is to store variables from a ``labor.workflow.Workflow`` instance. It is embedded as an attribute of the ``laboro.context.Context`` object.

  Returns:
    ``laboro.context.store.Store``
  """
  def __init__(self):
    self.storage = SimpleNamespace()
    self.step_item = None
    self.action_item = None
    self.method_item = None

  def put(self, prop, value):
    """Store the ``prop`` variable and its value.

    Arguments:
      prop: A string defining the variable name.
      value: Any object that will be stored as the ``prop`` variable value.

    Raises:
      ``TypeError``: When ``prop`` is not a string.
    """
    setattr(self.storage, prop, value)

  def get(self, prop):
    """Retrieve the ``prop`` variable value.

    Arguments:
      prop: A string defining the variable name.

    Returns:
      Any type depending of the ``prop`` value.

    Raises:
      ``AttributeError``: When ``prop`` does not exist within the Store instance.
      ``TypeError``: When ``prop`` is not a string.
    """
    return getattr(self.storage, prop)

  def clear(self):
    """Clear the Store content.
    """
    self.storage = SimpleNamespace()
    self.step_item = None
    self.action_item = None
    self.method_item = None

  def as_dict(self):
    return {key: value for key, value in self.storage.__dict__.items()}
