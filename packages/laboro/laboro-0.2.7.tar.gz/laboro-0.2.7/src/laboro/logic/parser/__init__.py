import logging
from ast import literal_eval
from asteval import Interpreter
from laboro.logger import LaboroLogger

logging.setLoggerClass(LaboroLogger)
logger = logging.getLogger("laboro.main")


class Parser:
  @staticmethod
  def parse(obj, store):
    res = obj
    if isinstance(obj, str):
      return Parser().eval(obj, store)
    elif isinstance(obj, dict):
      res = {key: Parser().parse(value, store) for key, value in res.items()}
    elif isinstance(obj, (list, tuple)):
      res = [Parser().parse(item, store) for item in res]
      if isinstance(obj, tuple):
        res = tuple(res)
    return res

  @staticmethod
  def eval(expression, store):
    if isinstance(expression, str):
      try:
        res = Interpreter(usersyms=store).eval(expression,
                                               raise_errors=True,
                                               show_errors=False)
      except (KeyError, TypeError, ValueError, SyntaxError, NameError):
        return expression
      if isinstance(res, str):
        return Parser().literal_eval(res)
      return Parser().parse(res, store)
    return expression

  @staticmethod
  def literal_eval(expression):
    try:
      return literal_eval(expression)
    except (KeyError, TypeError, ValueError, SyntaxError, NameError):
      return expression
