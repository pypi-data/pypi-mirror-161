import copy
from laboro.error import LaboroError
from laboro.logic.processor import Processor
from laboro.context import Context as BaseContext


class Context(BaseContext):
  """The ``laboro.context.method.Context`` object manages all low level tasks for ``laboro.workflow.Method`` instances. It is instantiated once per ``Method``.

  Its main purpose are:
    - Register method secrets
    - Set and return `$method_item$` values.

  Arguments:
    ``log_mgr``: A ``laboro.logger.manager.Manager`` instance.
    ``config_mgr``: A ``laboro.config.manager.Manager`` instance.

  Returns:
    ``laboro.context.method.Context``
  """
  def __init__(self, parent):
    super().__init__(log_mgr=parent.log_mgr, config_mgr=parent.config_mgr)
    self.parent = parent
    self.module_mgr = self.parent.module_mgr
    self.workspace = self.parent.workspace

  def register_method_secrets(self, instance, method, args):
    """Register the secrets from the specified arguments ``args``.
    Retrieve the name of the ``instance``'s ``method`` declared as *secret* and register their value in the ``laboro.Vault.vault`` embedded in the ``laboro.logger.LaboroLogger``.

    Arguments:
      instance: An instance of an object derived from the ``laboro.module.Module``.
      method: The ``instance`` method name from which retrieve the secret arguments list.
      args: A kwargs from which retrieve the secret value.

    Raises:
      ``laboro.error.LaboroError`` when the specified ``method`` does not exists.
    """
    if args is not None:
      try:
        method_spec = [meth for meth in instance.specification["methods"] if meth["name"] == method][0]
        if method_spec.get("args") is not None:
          spec_args = method_spec.get("args")
          secret_keys = [arg["name"] for arg in spec_args if arg["secret"]]
          secrets = [args[key]
                     for key in args.keys() if key in secret_keys]
          list(map(self.register_secret, secrets))
      except IndexError as err:
        raise LaboroError(f"UnknownMethodError: Unknown method {instance.__class__.__name__}.{method}") from err

  def get_method_args(self, args):
    if args is not None:
      interpolated = copy.deepcopy(args)
      for key, value in interpolated.items():
        interpolated[key] = Processor().process_arg(self, str(value))
      return interpolated
    return dict()

  def set_method_item(self, item):
    self._store.method_item = item

  def get_step_item(self):
    return self.parent.get_step_item()

  def get_action_item(self):
    return self.parent.get_action_item()

  def get_method_item(self):
    return self._store.method_item

  def store_as_dict(self):
    store = super().store_as_dict()
    store["step_item"] = self.get_step_item()
    store["action_item"] = self.get_action_item()
    store["method_item"] = self.get_method_item()
    return store
