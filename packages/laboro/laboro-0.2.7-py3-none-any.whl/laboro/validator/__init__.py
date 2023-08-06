import os
import copy
import yaml
from yamlinclude import YamlIncludeConstructor
import logging
import builtins
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError
from laboro.error import LaboroError
from laboro.logger import LaboroLogger

logging.setLoggerClass(LaboroLogger)
logger = logging.getLogger("laboro.main")


class Validator:
  """The ``laboro.validator.Validator`` object purpose is to validate `json` object against `jsonschema` specification given as `YAML` files.

  This object is instantiated by some **Laboro** core components and is **not intended to be used directly**.
  """

  def validate_from_files(self, schema, instance):
    """Validate the given instance against the given schema.

    Arguments:
    ``schema``: A file path to a *YAML* representation of a `jsonschema` representing the schema against which the ``instance`` should be validated.

    ``instance``: A file path to a *YAML* representation of a `json` representing the instance to validate.

    Raises:
      ``laboro.error.Error``: Whenever the schema or the instance file can't be loaded or are not valid *YAML* files. Error is also raised when the given ``schema`` is not a valid `jsonschema` or when ``instance`` can not validate against the given ``schema``.
    """
    try:
      schema_yml = self._load_file(schema)
      instance_yml = self._load_file(instance)
      validate(instance=instance_yml, schema=schema_yml)
      return instance_yml
    except ValidationError as err:
      msg = {"type": "InvalidSchemaInstanceError",
             "message": f"Instance is invalid: {err.message}"}
      logger.critical(f"[{msg['type']}] {msg['message']}")
      raise LaboroError(f"[{msg['type']}] {msg['message']}") from err
    except SchemaError as err:
      msg = {"type": "InvalidSchemaError",
             "message": f"Schema is invalid: {err.message}"}
      logger.critical(f"[{msg['type']}] {msg['message']}")
      raise LaboroError(f"[{msg['type']}] {msg['message']}") from err

  def validate_method_args(self, method, args):
    """Validate the method arguments against the method specification.

    Arguments:
      method: A dict describing the method specification from the module.
      args: A dict representing the method argument and their values.

    Raises:
      ``laboro.error.LaboroError``: When the given ``args`` does not validate against the specification.
    """
    try:
      if method.get("args") is None:
        if len(args) > 0:
          msg = {"type": "TooManyArgsError",
                 "message": f"Method does not accept args: {method['name']}"}
          logger.critical(f"[{msg['type']}] {msg['message']}")
          raise LaboroError(f"[{msg['type']}] {msg['message']}")
        return
      if not isinstance(args, dict):
        msg = f"[MethodArgError]: Expected dict, received {type(args)}"
        logger.critical(msg)
        raise LaboroError(msg)
      if not self._validate_required(args, method):
        msg = "[MissingRequiredArgError] Missing required argument."
        logger.critical(msg)
        raise LaboroError(msg)
      for arg, value in args.items():
        if arg in [arg["name"] for arg in method["args"]]:
          self._validate_type(arg, value, method)
          self._validate_implied(arg, args, method)
          self._validate_excluded(arg, args, method)
        else:
          msg = {"type": "UnknownMethodArgError",
                 "message": f"Unknown argument: {arg}"}
          logger.critical(f"[{msg['type']}] {msg['message']}")
          raise LaboroError(f"[{msg['type']}] {msg['message']}")
    except AttributeError as err:
      msg = {"type": "InvalidMethodSpecTypeError",
             "message": f"Specification must be dict. Received: {type(method)}"}
      logger.critical(f"[{msg['type']}] {msg['message']}")
      raise LaboroError(f"[{msg['type']}] {msg['message']}") from err

  def validate_obj_args(self, specification, args):
    """Validate the instantiation arguments against the object specification.

    Arguments:
      specification: A file path to a *YAML* representation of a `jsonschema` representing the schema against which the ``args`` should be validated.

      args: A dict representing the object instantiation argument and their values.

    Raises:
      ``laboro.error.LaboroError``: When the given ``args`` does not validate against the specification.
    """
    if not isinstance(args, dict):
      msg = f"[ModuleArgError]: Expected a dict as args, received {type(args)}"
      logger.critical(msg)
      raise LaboroError(msg)
    obj = self._load_file(specification)
    if obj.get("args") is None:
      if len(args) > 0:
        msg = {"type": "TooManyArgsError",
               "message": f"Object constructor does not accept args: {obj['class']}"}
        logger.critical(f"[{msg['type']}] {msg['message']}")
        raise LaboroError(f"[{msg['type']}] {msg['message']}")
      return
    if not self._validate_required(args, obj):
      msg = "[MissingRequiredArgError] Missing required argument."
      logger.critical(msg)
      raise LaboroError(msg)
    for arg, value in args.items():
      if arg in [arg["name"] for arg in obj["args"]]:
        self._validate_type(arg, value, obj)
        self._validate_implied(arg, args, obj)
        self._validate_excluded(arg, args, obj)
      else:
        msg = {"type": "UnknownObjArgError",
               "message": f"Unknown argument: {arg}"}
        logger.critical(f"[{msg['type']}] {msg['message']}")
        raise LaboroError(f"[{msg['type']}] {msg['message']}")

  def set_default_obj_args(self, specification, args):
    obj = self._load_file(specification)
    return self._set_default_args(obj, args)

  def set_default_method_args(self, method, args):
    return self._set_default_args(method, args)

  def _set_default_args(self, obj, args):
    if obj.get("args") is not None:
      default_args = copy.deepcopy(obj.get("args"))
      for arg in default_args:
        if arg.get("default") is not None:
          arg["value"] = arg["default"]
        if args.get(arg["name"]) is not None:
          arg["value"] = args.get(arg["name"])
      return {arg["name"]: arg["value"] for arg in default_args if arg.get("value") is not None}
    return args

  def _load_file(self, filepath):
    try:
      base_dir = os.path.dirname(filepath)
      YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader,
                                                 base_dir=base_dir)
      with open(filepath, mode="r", encoding="utf-8") as schema:

        return yaml.load(schema, Loader=yaml.FullLoader)
    except FileNotFoundError as err:
      msg = {"type": "FileNotFoundError",
             "message": f"File not found: {filepath}"}
      logger.critical(f"[{msg['type']}] {msg['message']}")
      raise LaboroError(f"[{msg['type']}] {msg['message']}") from err
    except(yaml.scanner.ScannerError,
           yaml.constructor.ConstructorError) as err:
      msg = {"type": "InvalidYamlError",
             "message": f"YAML file is invalid: {filepath}"}
      logger.critical(f"[{msg['type']}] {msg['message']}")
      raise LaboroError(f"[{msg['type']}] {msg['message']}") from err

  def _validate_required(self, arguments, specification):
    try:
      required = sorted([arg["name"] for arg in list(filter(lambda arg: arg["required"], specification["args"]))])
      return sorted([arg for arg in arguments if arg in required]) == required
    except Exception as err:
      raise LaboroError(f"[InvalidSpecError] Unable to validate required args: {err}") from err

  def _validate_type(self, arg, value, specification):
    arg_type = [aarg["type"] for aarg in specification["args"] if aarg["name"] == arg][0]
    required = [aarg["required"] for aarg in specification["args"] if aarg["name"] == arg][0]
    if required or value is not None:
      try:
        allowed_types = arg_type if isinstance(arg_type, list) else [arg_type]
        allow = [isinstance(value, getattr(builtins, allowed))
                 for allowed in allowed_types]
        if not any(allow):
          msg = {"type": "BadArgTypeError",
                 "message": f"Expected type one of {allowed_types} / received {type(value)} for {arg}."}
          logger.critical(f"[{msg['type']}] {msg['message']}")
          raise LaboroError(f"[{msg['type']}] {msg['message']}")
      except AttributeError as err:
        msg = {"type": "UnknownTypeError",
               "message": f"Unknown type '{arg_type}' for argument {arg}."}
        logger.critical(f"[{msg['type']}] {msg['message']}")
        raise LaboroError(f"[{msg['type']}] {msg['message']}") from err

  def _validate_implied(self, arg, arguments, specification):
    try:
      implied = sorted([aarg["implied"] for aarg in list(filter(lambda arg: arg["implied"], specification["args"])) if aarg["name"] == arg])[0]
    except IndexError:
      implied = list()
    if sorted([iarg for iarg in arguments if iarg in implied]) != implied:
      msg = {"type": "MissingImpliedArgError",
             "message": f"All args of {implied} are required by {arg}."}
      logger.critical(f"[{msg['type']}] {msg['message']}")
      raise LaboroError(f"[{msg['type']}] {msg['message']}")

  def _validate_excluded(self, arg, arguments, specification):
    try:
      excluded = sorted([aarg["excluded"] for aarg in list(filter(lambda arg: arg["excluded"], specification["args"])) if aarg["name"] == arg])[0]
    except IndexError:
      excluded = list()
    if len([earg for earg in arguments if earg in excluded]) > 0:
      msg = {"type": "ExcludedArgError",
             "message": f"None of {' or '.join(excluded)} can be used alongside {arg}."}
      logger.critical(f"[{msg['type']}] {msg['message']}")
      raise LaboroError(f"[{msg['type']}] {msg['message']}")
