import os
import time
import logging
import sqlite3
from datetime import datetime
from prettytable import PrettyTable

logger = logging.getLogger("laboro.main")


class History:
  """The ``laboro.history.History`` class provides all methods necessary to manage execution history. The history file is a `sqlite` database.

  Arguments:
      filename: A string specifying the full path to the history file to use
      workflow: A string defining the workflow name.
      session: A unique string defining the workflow execution session.
      params: A dict object listing all workflow parameters and their values.
      retention: An integer defining how many executions an history record should keep in the history file.

  Returns:
    ``laboro.history.History``: An history object.

  Raises:
    ``sqlite3.Error``: Any sqlite3 error may be raised when such an error occurs.
  """

  def __init__(self, filename, workflow, session, params, retention=90):
    self.hist_filename = filename
    self.workflow = workflow
    self.params = str(params)
    self.start = time.time()
    self.session = session
    self.retention = retention

  def _create_db(self):
    logger.info(f"[+] Checking history database: {self.hist_filename}")
    if not os.path.exists(self.hist_filename):
      with sqlite3.connect(self.hist_filename) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE executions (workflow, session TEXT, start REAL, end REAL, duration TEXT, params TEXT, exit_code INTEGER)")
        conn.commit()

  def _end_exec(self, exit_code):
    logger.info(f"[+] Registering end of session: [{self.session}]: {exit_code}")
    end = time.time()
    delta = datetime.fromtimestamp(end) - datetime.fromtimestamp(self.start)
    result = [end,
              self._format_time_delta(delta),
              exit_code,
              self.session]
    with sqlite3.connect(self.hist_filename) as conn:
      cursor = conn.cursor()
      cursor.execute("update executions set end=?, duration=?, exit_code=? where session=?", result)
      conn.commit()

  def _purge_history(self):
    """Purge history database."""
    logger.info(f"[+] Purging history: Keeping last {self.retention} executions")
    with sqlite3.connect(self.hist_filename) as conn:
      cursor = conn.cursor()
      cursor.execute("delete from executions where session not in (select session from executions order by end DESC limit ?)", [self.retention])
      conn.commit()

  def _format_time_delta(self, tdelta):
    """Take a timedelta object and formats it for humans.
    From https://gist.github.com/dhrrgn/7255361
    """
    delta = dict(days=tdelta.days)
    delta["hrs"], rem = divmod(tdelta.seconds, 3600)
    delta["min"], delta["sec"] = divmod(rem, 60)
    if delta["min"] == 0:
      fmt = "{sec} sec"
    elif delta["hrs"] == 0:
      fmt = "{min} min {sec} sec"
    elif delta["days"] == 0:
      fmt = "{hrs} hr(s) {min} min {sec} sec"
    else:
      fmt = "{days} day(s) {hrs} hr(s) {min} min {sec} sec"
    return fmt.format(**delta)

  def enter(self):
    """Start the ``laboro.history.History`` instance.
    Create the history file database if needed, purge the associated ``laboro.workflow.Workflow`` history execution and record the present execution parameters.

    Registered parameters are:
    - The workflow name
    - The workflow session
    - The start date timestamp
    - The workflow init parameters
    """
    self._create_db()
    self._purge_history()
    record = [self.workflow,
              self.session,
              self.start,
              self.params]
    with sqlite3.connect(self.hist_filename) as conn:
      cursor = conn.cursor()
      cursor.execute("insert into executions (workflow, session, start, params) values (?, ?, ?, ?)", record)
      conn.commit()

  def exit(self, kind, value):
    """Exit the ``laboro.history.History`` instance.
    When exiting, the ``laboro.history.History`` instance records the end date timestamp, the time delta between execution start and end the exit code type and its value.

    Arguments:
      kind: The kind of event that triggered the exit. Its type is variable.
      value: The value of the event that triggered the exit. Its type depends on the ``kind`` type.
    """
    exit_code = 0
    if kind == SystemExit:
      if value.code is not None:
        exit_code = value.code
    elif kind is not None:
      exit_code = f"{kind.__name__}: {value}"
    self._end_exec(exit_code)

  def read_history(self, workflow, num_exec):
    """Displays last ``num_exec`` history lines for specified ``workflow``.

    At this point, this method is not used by **Laboro** itself. It may be accessible in a future version of **Laboro**.

    Arguments:
      workflow: A string representing the workflow name to search for.
      num_exec: An integer representing the number of executions to retrieve.

    Returns:
      ``str``: A string representation of the history displayable as a PrettyTable.
    """
    table = PrettyTable()
    table.field_names = ["Workflow",
                         "Session",
                         "Start",
                         "End",
                         "Duration",
                         "Params",
                         "Exit"]
    with sqlite3.connect(self.hist_filename) as conn:
      cursor = conn.cursor()
      cursor.execute("select * from executions where workflow=? order by start desc limit ?", [workflow, num_exec])
      table.add_rows(cursor.fetchall())
      return table.get_string()
