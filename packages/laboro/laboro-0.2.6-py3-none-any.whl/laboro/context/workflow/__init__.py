import os
from laboro.context import Context as Ctx
from laboro.history import History
from laboro.workspace import Workspace
from laboro.module.manager import Manager as ModuleMgr
from laboro.error.handler import Handler as ErrorHandler


class Context(Ctx):
  """The ``laboro.context.workflow.Context`` object manages all low level tasks for ``laboro.workflow.Workflow`` instances. It is instantiated once by the main **Laboro** process and is passed from **Workflow** instances to **Workflow** instances.

  It loads the main **Laboro** configuration file and initiate all needed **Laboro** submodules.

  Arguments:
    ``log_mgr``: A ``laboro.logger.manager.Manager`` instance.
    ``config_mgr``: A ``laboro.config.manager.Manager`` instance.

  Raises:
    ``laboro.error.LaboroError``: If the main **Laboro** configuration file is not found or invalid.

  Returns:
    ``laboro.context.workflow.Context``
  """
  def __init__(self, log_mgr, config_mgr):
    super().__init__(log_mgr, config_mgr)
    self.delete_workspace_on_exit = True
    self.history = None
    self.module_mgr = ModuleMgr()
    self.config_mgr = config_mgr
    self.workspacedir = self.config_mgr.get_parameter("main",
                                                      "$.laboro.workspacedir")
    self.histdir = self.config_mgr.get_parameter("main",
                                                 "$.laboro.histdir")
    self.workflowdir = self.config_mgr.get_parameter("main",
                                                     "$.laboro.workflowdir")
    self.logdir = self.config_mgr.get_parameter("main",
                                                "$.laboro.log.dir")
    self.loglevel = self.config_mgr.get_parameter("main",
                                                  "$.laboro.log.level")
    self.workflow_name = None
    self.workflow_session = None
    self.workspace = None
    self.parent = None

  def reset(self, session, workspace_cfg):
    """Reset the ``laboro.context.Context`` instance with the new workflow configuration and session.

    Arguments:
      session: A unique string defining a workflow session. Usually a string representation of a uuid.uuid4() instance.
      workspace_cfg: A dict representing the workspace configuration. See ``laboro.workspace.Workspace`` and ``laboro.workflow.Workflow`` for workspace configuration details.

    Raises:
      ``laboro.error.LaboroError``: For various reasons linked to the submodules instantiations.

    Returns:
      ``laboro.context.Context``: The ``Context`` instance reset with the new parameters.
    """
    if self.parent is None:
      try:
        self.workflow_session = session
        self.workflow_name = self.config_mgr.get_parameter("workflow", "$.name")
        self.workflow_name = self.workflow_name.replace(" ", "_")
        self._configure_logger()
        start_msg = f"Started {self.workflow_name} / {self.workflow_session}"
        self.log.log_section("WORKFLOW", start_msg)
        self.log.vault.clear()
        self._store.clear()
        self.delete_workspace_on_exit = workspace_cfg["delete_on_exit"]
        self.workspace = Workspace(workspacedir=self.workspacedir,
                                   workflow=self.workflow_name,
                                   session=self.workflow_session)
        history_path = os.path.join(self.histdir, f"{self.workflow_name}.db")
        self.history = History(filename=history_path,
                               workflow=self.workflow_name,
                               session=self.workflow_session,
                               params=self.config_mgr.workflow_config)
        self.history.enter()
        self.install_packages()
        return self
      except Exception as err:
        ErrorHandler().handle_error(self.workflow_name,
                                    self.workflow_session,
                                    err.__class__,
                                    str(err))

  def exit(self, kind, value):
    """Exit the ``Context`` instance.
    When the instance exit, it triggers the ``laboro.workspace.Workspace``, ``laboro.history.History`` instances exit and close the log linked to the ``laboro.workflow.Workflow`` instance associated with the ``Context`` instance. It also register the exit/error code.

    Arguments:
      kind: The kind of event that triggered the ``Context`` instance exit.
      value: The `value` of the event that triggered the ``Context`` instance exit.
    """
    if self.delete_workspace_on_exit:
      self.workspace.delete()
    self.history.exit(kind, value)
    ErrorHandler().handle_error(self.workflow_name,
                                self.workflow_session,
                                kind,
                                value)
    self.log_mgr.remove_file_handler(self.workflow_session)

  def _configure_logger(self):
    self.log_mgr.add_file_handler(self.logdir,
                                  self.workflow_name,
                                  self.workflow_session)
    self.log_mgr.set_log_level(self.loglevel)

  def install_packages(self):
    """Install all packages listed in the workflow configuration file.
    """
    packages = self.config_mgr.get_parameter("workflow", "$.packages")
    for pkg in packages:
      self.module_mgr.install_package(pkg)
