import os
import shutil
import logging
from laboro.error import LaboroError
from laboro.logger import LaboroLogger

logging.setLoggerClass(LaboroLogger)
logger = logging.getLogger("laboro.main")


class Workspace:
  """The ``laboro.workspace.Workspace`` object manages the `laboro.workflow.`workflow`` instance workspace.

  The workflow workspace is a directory named after the workflow name within the **Laboro** global ``workspacedir`` directory.

  Each workflow execution has its own sub-directory  named after the workflow session.

  A ``Workspace`` instance is used to store files within the workflow execution.

  Arguments:
    workspacedir: A string defining the directory where all workspaces are stored.
    workflow: A string defining the workflow name.
    session: A unique string defining the workflow execution session.

  Returns:
    ``laboro.workspace.Workspace``: The workspace for the workflow session.

  Raises:
    ``laboro.error.LaboroError``: When any error such as *OSError* while creating the workspace occurs.
  """
  def __init__(self, workspacedir, workflow, session):
    try:
      self.workspace_dir = os.path.join(workspacedir, workflow)
      self.workspace_path = os.path.join(workspacedir, workflow, session)
      logger.info(f"[+] Creating workspace: {self.workspace_path}")
      os.makedirs(self.workspace_path)
    except Exception as err:
      raise LaboroError(f"[{err.__class__.__name__}] {str(err)}") from err

  def data_to_file(self, filename, data, mode="w",
                   encoding=None, offset=0, whence=0):
    filename = os.path.join(self.workspace_path, filename)
    logger.info(f"Saving file: {filename} ({mode} / {encoding} / ({offset}, {whence}))")
    with open(filename, mode=mode, encoding=encoding) as datafile:
      datafile.seek(offset, whence)
      datafile.write(data)

  def data_from_file(self, filename, length=None, mode="r",
                     encoding=None, offset=0, whence=0):
    filename = os.path.join(self.workspace_path, filename)
    logger.info(f"Reading file: {filename} ({mode} / {encoding} / ({offset}, {whence}))")
    with open(filename, mode=mode, encoding=encoding) as datafile:
      datafile.seek(offset, whence)
      return datafile.read(length)

  def stream_from_file(self, filename, mode="r", encoding=None):
    filename = os.path.join(self.workspace_path, filename)
    logger.info(f"Getting bytestream: {filename} ({mode} / {encoding})")
    return open(filename, mode=mode, encoding=encoding)

  def delete(self):
    """Deletes the instance workspace and all its content.
    This will **not** delete the workflow workspace.

    Raises:
      ``laboro.error.LaboroError``: When any error such as *OSError* while creating the workspace occurs.
    """
    logger.info(f"[+] Deleting workspace: {self.workspace_path}")
    try:
      shutil.rmtree(self.workspace_path)
    except Exception as err:
      raise LaboroError(f"[{err.__class__.__name__}] {str(err)}") from err
