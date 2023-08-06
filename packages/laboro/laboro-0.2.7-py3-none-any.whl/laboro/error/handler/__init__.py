import logging
import traceback
from laboro.logger import LaboroLogger

logging.setLoggerClass(LaboroLogger)
logger = logging.getLogger("laboro.main")


class Handler:
  """The ``laboro.error.handler.Handler`` is a singleton that logs every event given to its ``handle_error()`` method.
  """

  @staticmethod
  def handle_error(name, session, kind, value):
    """Log the given error with its traceback and exit.

    Arguments:
      name: A string specifying the ``laboro.workflow.Workflow`` instance name.
      session: A string specifying the ``laboro.workflow.Workflow`` instance session.
      kind: The `kind` of event. The type of `kind` is variable.
      value: The value of the event. The type of `value` depends on `kind`.
    """
    level = logging.INFO
    exit_msg = "Exited"
    exit_code = 0
    if kind == SystemExit:
      if value.code is not None:
        exit_code = value.code
    elif kind is not None:
      level = logging.CRITICAL
      exit_code = f"{kind.__name__}: {value}"
    exit_msg += f" {name} / {session} with {exit_code}"
    logger.log_section("WORKFLOW", exit_msg, level=level)
    if kind is not None and kind != SystemExit:
      if logger.getEffectiveLevel() <= logging.DEBUG:
        traceback.print_exc()
