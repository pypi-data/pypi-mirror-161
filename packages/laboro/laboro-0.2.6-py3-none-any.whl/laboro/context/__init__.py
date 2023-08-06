import copy
from laboro.context.store import Store
from laboro.logic.processor import Processor


class Context:
  """The ``laboro.context.Context`` class is the base class of ``laboro.context.workflow.Context``, ``laboro.context.step.Context``, ``laboro.context.action.Context`` and ``laboro.context.method.Context``.

  It provides a ``laboro.context.store.Store`` object to store object, variables. It also register `secrets` to `logger`'s `vault` instance.

  Its main purpose is:
    - Register modules to the workflow ``ModuleManager`` instance
    - Instantiate object (with instance secrets registration)
    - Store instantiated objects in its ``Store`` instance

  Arguments:
    logger: A ``laboro.logger.manager.Manager`` instance.
    config_mgr: A ``laboro.config.manager.Manager`` instance.

  Returns:
    ``laboro.context.Context``
  """
  @property
  def log(self):
    return self.log_mgr.logger

  @property
  def store(self):
    return self.store_as_dict()

  def __init__(self, log_mgr, config_mgr):
    self.config_mgr = config_mgr
    self.log_mgr = log_mgr
    self.parent = None
    self.workspace = None
    self.module_mgr = None
    self._store = Store()

  def exit(self, kind, value):
    """Exit the ``Context`` instance.

    The exit method is simply a call to the parent context.
    Subclasses of the Context class may redefine this method.

    Arguments:
      kind: The kind of event that triggered the ``Context`` instance exit.
      value: The `value` of the event that triggered the ``Context`` instance exit.
    """
    if self.parent is not None:
      self.parent.exit(kind, value)

  def put(self, prop, value):
    """Store the ``prop`` variable and its value in the ``Context.store`` ``laboro.context.Store`` instance.

    Arguments:
      prop: A string representing the variable name.
      value: Any type, the value to store.

    Raises:
      ``TypeError``: When ``prop`` is not a string.
    """
    if self.parent is not None:
      self.parent.put(prop, value)
    else:
      self._store.put(prop, value)

  def get(self, prop):
    """Return the value of ``prop`` from the store instance. When ``prop`` is not found in the store, return the ``prop`` value from the parent store if any.

    Arguments:
      prop: A string representing the variable name.

    Raises:
      ``TypeError``: When ``prop`` is not a string.
      ``AttributeError``: When ``prop`` does not exist within the Store instance nor within the parent Context store.
    """
    try:
      return self._store.get(prop)
    except AttributeError as err:
      if self.parent is not None:
        return self.parent.get(prop)
      raise err

  def register_class(self, module, cls):
    """Register to the `module manager` the specified class from the specified module.

    Arguments:
      ``module``: The python module name from which the class is.
      ``class``: The class name.
    """
    self.module_mgr.register_class_from_module(cls, module)

  def instantiate(self, name, module, cls, args):
    """Register the class to the ``laboro.module.ModuleMgr`` instance and store the instance into the store for later use.

    Arguments:
      module: A string specifying the *Python* module name from each retrieve the class.
      cls: A string specifying the class name to instantiate.
      args: A `kwargs` that will be used to instantiate the class.

    Returns:
      An instance of the class ``module``.``cls`` instantiated with the ``args`` `kwargs` as init parameters.

    Raises:
      ``laboro.error.LaboroError``: When the specified module or class ar not available and when the specified ``args`` are incompatibles with the class constructor.
    """
    self.log.info(f"[+] Object instantiation: [{name}] {module}.{cls}")
    obj = self.module_mgr.get_class_from_module(cls=cls, module=module)
    instance_args = self._get_instance_args(args=args)
    with obj(context=self, args=instance_args) as instance:
      self._register_instance_secrets(instance, instance_args)
      self.put(name, instance)

  def register_secret(self, secret):
    """Register the given secret to logger's ``laboro.vault.Vault`` instance.
    """
    self.log.vault.add(secret)

  def store_as_dict(self):
    parent_store = {}
    if self.parent is not None:
      parent_store = self.parent.store_as_dict()
    store = self._store.as_dict()
    for key, value in parent_store.items():
      if key not in store:
        store[key] = value
    return store

  def _register_instance_secrets(self, instance, args):
    if instance.specification.get("args") is not None and args is not None:
      class_args = instance.specification.get("args")
      secret_keys = [arg["name"] for arg in class_args if arg["secret"]]
      secrets = [args[key] for key in args.keys() if key in secret_keys]
      list(map(self.register_secret, secrets))

  def _get_instance_args(self, args=None):
    if args is not None:
      interpolated = copy.deepcopy(args)
      for key, value in interpolated.items():
        interpolated[key] = Processor().process_arg(self, str(value))
      return interpolated
    return dict()
