from laboro.context import Context as BaseContext


class Context(BaseContext):
  """The ``laboro.context.step.Context`` object manages all low level tasks for ``laboro.workflow.Step`` instances. It is instantiated once per ``Step`` instance.

  Its main purpose is:
    - Register modules to the workflow ``ModuleManager`` instance
    - Instantiate object (with instance secrets registration)
    - set and return `$step_item$` values.

  Arguments:
    ``log_mgr``: A ``laboro.logger.manager.Manager`` instance.
    ``config_mgr``: A ``laboro.config.manager.Manager`` instance.

  Returns:
    ``laboro.context.step.Context``"""
  def __init__(self, parent):
    super().__init__(log_mgr=parent.log_mgr, config_mgr=parent.config_mgr)
    self.parent = parent
    self.module_mgr = self.parent.module_mgr
    self.workspace = self.parent.workspace

  def set_step_item(self, item):
    self._store.step_item = item

  def get_step_item(self):
    return self._store.step_item

  def get_action_item(self):
    return None

  def get_method_item(self):
    return None

  def store_as_dict(self):
    store = super().store_as_dict()
    store["step_item"] = self.get_step_item()
    store["action_item"] = None
    store["method_item"] = None
    return store
