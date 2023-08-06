import os
import logging
from jsonpath import JSONPath
from laboro.error import LaboroError
from laboro.validator import Validator


class Manager:
  """The ``laboro.config.manager.Manager`` object loads and check all configuration files needed by  **Laboro** to operate.

  Arguments:
    `main_config`: A string representing the main **Laboro** configuration filename.

  Returns:
    ``laboro.config.manager.Manager``: The **Laboro** configuration manager.

  Raises:
    ``laboro.error.LaboroError``: When one of the configuration files are not found.
  """

  @property
  def main_config(self):
    """Get the ``main_config`` as a dict."""
    return self._main_config

  @property
  def workflow_config(self):
    """Get the ``workflow_config`` as a dict."""
    return self._workflow_config

  @main_config.setter
  def main_config(self, filename):
    """Set the main_config from a YAML file.

    Arguments:
      filename: A string specifying the YAML file to load the configuration from."""
    schema = os.path.join(os.path.dirname(__file__),
                          "schema",
                          "main.yml")
    self._main_config = Validator().validate_from_files(schema=schema,
                                                        instance=filename)

  @workflow_config.setter
  def workflow_config(self, filename):
    """Set the workflow_config from a YAML file.

    Arguments:
      filename: A string specifying the YAML file to load the configuration from."""
    schema = os.path.join(os.path.dirname(__file__),
                          "schema",
                          "workflow.yml")
    wkf_cfg = os.path.join(self.get_parameter("main", "$.laboro.workflowdir"),
                           filename)
    self._workflow_config = Validator().validate_from_files(schema=schema,
                                                            instance=wkf_cfg)

  def __init__(self, main_config):
    self.main_config = main_config
    self._workflow_config = dict()

  def get_parameter(self, level, param):
    """Returns the configuration parameter specified by ``param`` from the configuration ``level``.

    Arguments:
      level: A string that specify the level from which retrieve the parameter. Must be one of ``main`` or ``workflow``.
      param: A string that specify the parameter name as described by the JSONPath spec. The ``param`` argument is in `dotted` format.

    Returns:
      Any type, depending on `YAML` file from which the configuration is generated.

    Raises:
      ``laboro.error.LaboroError``: When the specified parameter is unknown or ``level`` value is not valid.

    ..  code-block:: python

        manager = Manager(main_conf)
        manager.get_parameter("workflow",
                              "$.steps[0].actions[0].instance.args.my_arg")
    """
    levels = {"main": self.main_config,
              "workflow": self.workflow_config}
    try:
      config = levels[level]
      try:
        return JSONPath(param).parse(config)[0]
      except IndexError as err:
        msg = f"UnknownParameterError: [{level}]: {param}"
        logging.critical(msg)
        raise LaboroError(msg) from err
    except KeyError as err:
      msg = f"BadConfLevelError: Bad configuration level: {level}"
      logging.critical(msg)
      raise LaboroError(msg) from err
