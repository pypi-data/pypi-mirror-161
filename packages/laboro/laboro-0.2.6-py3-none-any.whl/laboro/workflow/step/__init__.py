from laboro.context.action import Context as ActionContext
from laboro.logic.processor import Processor
from laboro.workflow.action import Action


class Step:
  """The ``laboro.workflow.step.Step`` object is the object representation of a workflow step.

  Arguments:
    context: The ``laboro.context.Context`` instance used by the workflow.
    name: A string, specifying the step name.
    actions: A list, the list of the step actions
    when: Optional. A string representation of an expression thant can be evaluate as a boolean.
    loop: Optional. A string describing any iterable object.

  Returns:
    ``laboro.workflow.step.Step``

  """
  @property
  def iterable(self):
    """Get the *iterable* object on which loop, if any.
    This property is evaluated for each call from the ``loop`` attribute.
    """
    if self.loop is not None:
      return Processor().process(self.ctx, str(self.loop))
    return [self.loop]

  @property
  def runnable(self):
    """Get the condition in which the step is runnable.
    This property is evaluated for each call from the ``when`` attribute.
    """
    if self.when is not None:
      return Processor().process(self.ctx, str(self.when))
    return True

  def __init__(self, context, name, actions,
               instances=None, when=None, loop=None):
    self.name = name
    self.ctx = context
    self.instances = instances
    if instances is None:
      self.instances = list()
    self.when = when
    self.loop = loop
    self.actions = actions

  def __enter__(self):
    return self

  def __exit__(self, kind, value, traceback):
    pass

  def _instantiate(self, instance):
    self.ctx.register_class(module=instance.get("module"),
                            cls=instance.get("class"))
    self.ctx.instantiate(module=instance.get("module"),
                         cls=instance.get("class"),
                         name=instance.get("name"),
                         args=instance.get("args"))

  def run(self):
    """Run the step.
    Calling ``laboro.workflow.step.Step.run()`` will run all actions within the step if the ``runnable`` property evaluate to ``True``.
    The actions within the step will be executed for each item in the ``iterable`` property.
    """
    self.ctx.log.log_section("STEP", self.name)
    for instance in self.instances:
      self._instantiate(instance)
    for item in self.iterable:
      self.ctx.set_step_item(item)
      if self.runnable:
        for step_action in self.actions:
          with Action(ActionContext(parent=self.ctx),
                      **step_action) as action:
            action.run()
      else:
        msg = f"Skipping {self.name}: Condition not met: {self.when}"
        self.ctx.log.warning(msg)
