import uuid
from laboro.context.step import Context as StepContext
from laboro.workflow.step import Step


class Workflow:
  """The ``laboro.workflow.Workflow`` object is the main class for the workflow representation.
  It load all configuration needed, set alk objects such History, Vault and workspace and run according to its configuration.

  The Workflow object provides a runtime context that will handle log, history, vault, and workspace, etc.

  Arguments:
    name: A string representing the workflow name.
    context: A ``laboro.context.Context`` instance.
    name: A string specifying the name of the workflow
    packages: A list of package names.
    workspace: A dictionary representation of a workspace configuration (see ``laboro.workspace.Workspace`` for further dertails).
    steps: A list of dictionary representation of ``laboro.workflow.Step``

  Returns:
    ``laboro.workflow.Workflow``: A Workflow object.

  ..  code-block:: python

      from laboro.vault import Vault()
      from laboro.log.manager import Manager as LogMgr
      from laboro.context import Context
      from laboro.workflow import Workflow

      cfg_mgr = CfgMgr(main_config="/etc/laboro/laboro.yml")
      context = Context(logger=LogMgr(Vault()), config_mgr=cfg_mgr)
      self.ctx.log.log_section("LABORO", "Bootstrapping")
      self.ctx.log.vault.clear()
      cfg_mgr.workflow_config = "my_workflow.yml"
      workflow_config = cfg_mgr.workflow_config
      with Workflow(context=context, **workflow_config) as wkf:
        wkf.run()
        ...
  """
  def __init__(self, context, name, packages, workspace,
               steps, log_level=None, instances=None):
    self.name = name.replace(" ", "_")
    self.packages = packages
    self.workspace = workspace
    self.steps = steps
    self.instances = instances
    if instances is None:
      self.instances = list()
    self.ctx = context.reset(session=str(uuid.uuid4()),
                             workspace_cfg=self.workspace,
                             log_level=log_level)

  def __enter__(self):
    return self

  def __exit__(self, kind, value, traceback):
    self.ctx.exit(kind, value)

  def _instantiate(self, instance):
    self.ctx.register_class(module=instance.get("module"),
                            cls=instance.get("class"))
    self.ctx.instantiate(module=instance.get("module"),
                         cls=instance.get("class"),
                         name=instance.get("name"),
                         args=instance.get("args"))

  def run(self):
    """Run the workflow."""
    for instance in self.instances:
      self._instantiate(instance)
    for wkf_step in self.steps:
      with Step(StepContext(parent=self.ctx),
                **wkf_step) as step:
        step.run()
    self.ctx.log.log_line()
