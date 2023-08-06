from laboro.logic.processor import Processor
from laboro.workflow.method import Method
from laboro.context.method import Context as MethodContext


class Action:
  """The ``laboro.workflow.action.Action`` object is a representation of a   ``laboro.workflow.step.Step`` action.

  Arguments:
    context: The ``laboro.context.Context`` instance used by the workflow.
    name: A string, specifying the action name.
    instance: A dictionary representation of ``instance`` as specified in the ``laboro.workflow.Workflow`` specification.
    when: Optional. A string representation of an expression thant can be evaluate as a boolean.
    loop: Optional. A string describing any iterable object.

  Returns:
    ``laboro.workflow.action.Action``
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

  def __init__(self, context, name, methods,
               instances=None, when=None, loop=None):
    self.name = name
    self.ctx = context
    self.when = when
    self.loop = loop
    self.instances = instances
    if instances is None:
      self.instances = list()
    self.methods = methods

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
    """Run the action.
    If the ``runnable`` property evaluate to ``True``, calling the ``run()`` method will instantiate the instance when needed and run all ``methods`` within the instance methods list.
    The methods within instance methods list will be executed for each item in the ``iterable`` property.
    """
    self.ctx.log.log_section("ACTION", self.name)
    for instance in self.instances:
      self._instantiate(instance)
    for item in self.iterable:
      self.ctx.set_action_item(item)
      if self.runnable:
        for action_method in self.methods:
          with Method(MethodContext(parent=self.ctx),
                      **action_method) as method:
            method.run()
      else:
        msg = f"Skipping {self.name}: Condition not met: {self.when}"
        self.ctx.log.warning(msg)
