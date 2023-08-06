from laboro.context import Context as BaseContext


class Context(BaseContext):
  """The ``laboro.context.action.Context`` object manages all low level tasks for ``laboro.workflow.Action`` instances. It is instantiated once per ``Action``.

  Its main purpose is:
    - Register modules to the workflow ``ModuleManager`` instance
    - Instantiate object (with instance secrets registration)
    - Set and return `$action_item$` values.

  Arguments:
    ``log_mgr``: A ``laboro.logger.manager.Manager`` instance.
    ``config_mg``r: A ``laboro.config.manager.Manager`` instance.

  Returns:
    ``laboro.context.action.Context``
  """
  def __init__(self, parent):
    super().__init__(log_mgr=parent.log_mgr, config_mgr=parent.config_mgr)
    self.parent = parent
    self.module_mgr = self.parent.module_mgr
    self.workspace = self.parent.workspace

  def set_action_item(self, item):
    self._store.action_item = item

  def get_step_item(self):
    return self.parent.get_step_item()

  def get_action_item(self):
    return self._store.action_item

  def get_method_item(self):
    return None

  def store_as_dict(self):
    store = super().store_as_dict()
    store["step_item"] = self.get_step_item()
    store["action_item"] = self.get_action_item()
    store["method_item"] = None
    return store
