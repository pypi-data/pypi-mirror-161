import re
import logging
from laboro.logic.parser import Parser
from laboro.logger import LaboroLogger

logging.setLoggerClass(LaboroLogger)
logger = logging.getLogger("laboro.main")


class Processor:
  @staticmethod
  def process(context, statement):
    file_ptn = re.compile(r"\$file\$")
    filepath = f"{context.workspace.workspace_path}/"
    statement = re.sub(file_ptn, filepath, statement)
    datafile_ptn = re.compile(r"\$datafile\$")
    datafile_path = f"{context.workspace.workspace_dir}/"
    statement = re.sub(datafile_ptn, datafile_path, statement)
    crypt_ptn = re.compile(r"\$crypt\$[^!.?,;\'\"\(\)\{\}\+\\\|\&<>\[\]\s]+")
    for encrypted in [enc.replace("$crypt$", "")
                      for enc in re.findall(crypt_ptn, statement)]:
      statement = statement.replace(f"$crypt${encrypted}",
                                    context.crypto.decrypt(encrypted))
    return Parser().parse(statement, context.store_as_dict())

  @staticmethod
  def process_arg(context, value):
    file_ptn = re.compile(r"\$file\$")
    filepath = f"{context.workspace.workspace_path}/"
    value = re.sub(file_ptn, filepath, value)
    datafile_ptn = re.compile(r"\$datafile\$")
    datafile_path = f"{context.workspace.workspace_dir}/"
    crypt_ptn = re.compile(r"\$crypt\$[^!.?,;\'\"\(\)\{\}\+\\\|\&<>\[\]\s]+")
    for encrypted in [enc.replace("$crypt$", "")
                      for enc in re.findall(crypt_ptn, value)]:
      value = value.replace(f"$crypt${encrypted}",
                            context.crypto.decrypt(encrypted))
    value = re.sub(datafile_ptn, datafile_path, value)
    return Parser().parse(value, context.store_as_dict())
