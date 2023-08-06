import re
import sys
import logging
import importlib
import subprocess
from laboro.error import LaboroError
from laboro.logger import LaboroLogger

logging.setLoggerClass(LaboroLogger)
logger = logging.getLogger("laboro.main")


class Manager:
  """The ``laboro.module.manager.Manager`` object manages all aspect of module handling such as package installation, module loading and module registration.
  """
  modules = dict()

  def install_package(self, package):
    """Install the specified *Python* package.

    Arguments:
      package: A string specifying the *Python* package name to install. i.e ``laboro_database``.

    Raises:
      ``laboro.error.LaboroError``: When the specified package is not available.
    """
    try:
      reg = re.compile("^laboro_.*$|^laboro-.*$")
      if re.match(reg, package) is not None:
        logger.info(f"[+] Installing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "-qqq", "install", package])
      else:
        logger.critical(f"Package is not a valid Laboro package: {package}")
        raise LaboroError(f"InvalidPackageNameError: Package is not a valid Laboro package: {package}")
    except subprocess.CalledProcessError as err:
      logger.critical(f"Unable to install Laboro package: {package}")
      raise LaboroError(f"InstallPackageError: Unable to install Laboro package: {package}") from err

  def register_class_from_module(self, cls, module):
    """Registers the ``cls`` class from the python module whose name is specified by the ``module`` argument.

    Once registered the specified ``cls`` will be accessible through the ``modules`` attribute.

    Registering a module is used to import external Laboro modules.

    To prevent abusive standard Python packages imports, module name defined by the ``module`` argument must match the following regular expression: ``^laboro_.*``.

    Arguments:
      cls: A string specifying the class to import from ``module``.
      module: A string specifying the module name from which import the ``cls`` class. The ``module`` name  **must** match ``^laboro_.*``.

    Raises:
      ``laboro.error.LaboroError``: When an ImportError occurred while attempting to register an unknown class or a class from an unknown module.

    In the following example illustrate how to import the ``PgClient`` class from the ``laboro_database.clients`` package.

    ..  code-block:: python

      from laboro.module.manager import Manager

      module_mgr = Manager()
      module_mgr.install_package(laboro_database)
      module_mgr.register(cls="PgClient", module="laboro_database.clients")

    """
    try:
      mod = importlib.import_module(module)
      if not hasattr(mod, cls):
        raise LaboroError(f"ClassNotFoundError: No such class: {module}.{cls}")
      if self.modules.get(module) is not None:
        if self.modules[module].get(cls) is None:
          logger.info(f"[+] Registering class: {module}.{cls}")
          self.modules[module][cls] = getattr(mod, cls)
      else:
        logger.info(f"[+] Registering class: {module}.{cls}")
        self.modules[module] = dict()
        self.modules[module][cls] = getattr(mod, cls)
    except ImportError as err:
      logger.critical(f"No such module: {module}")
      raise LaboroError(f"ModuleNotFoundError: No such module: {module}") from err

  def get_class_from_module(self, cls, module):
    """Return the specified registered class.

    Arguments:
      cls: A string specifying the class to retrieve.
      module: A string specifying the module to retrieve the class from.

    Raises:
      ``laboro.error.LaboroError``: When the specified module or class is unregistered.
    """
    try:
      return self.modules[module][cls]
    except KeyError as err:
      logger.critical(f"No such class: {module}.{cls}")
      raise LaboroError(f"UnregisteredClassError: No such class: {module}.{cls}") from err
