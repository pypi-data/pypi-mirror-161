import sys
import argparse
from laboro.context.workflow import Context
from laboro.config.manager import Manager as CfgMgr
from laboro.workflow import Workflow
from laboro.logger.manager import Manager as LogMgr
from laboro.interactive import encrypt
from laboro.interactive import decrypt


def run(context, cfg_mgr):
  try:
    with Workflow(context=context, **cfg_mgr.workflow_config) as wkf:
      wkf.run()
  except Exception:
    pass


def main(workflows, keyfile=None):
  crypto_key = keyfile
  if keyfile is not None:
    with open(keyfile, mode="r", encoding="utf-8") as key:
      crypto_key = key.readline().strip()
  cfg_mgr = CfgMgr(main_config="/etc/laboro/laboro.yml")
  log_mgr = LogMgr()
  context = Context(log_mgr=log_mgr,
                    config_mgr=cfg_mgr,
                    crypto_key=crypto_key)
  log_mgr.logger.log_section("LABORO", "Bootstrapping")
  for workflow_cfg in workflows:
    log_mgr.logger.vault.clear()
    cfg_mgr.workflow_config = workflow_cfg
    run(context=context, cfg_mgr=cfg_mgr)


def interactive_mode(args):
  if args.encrypt:
    encrypt.main()
  elif args.decrypt:
    decrypt.main()


def laboro_help(parser):
  parser.print_help()
  sys.exit(1)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Laboro CLI",
                                   prog="laboro")
  interactive_group = parser.add_argument_group(
      title="Interactive mode",
      description="Options for interactive mode")
  run_group = parser.add_argument_group(
      title="Run mode",
      description="Options for running workflows")
  interactive_options = interactive_group.add_mutually_exclusive_group()
  interactive_options.add_argument("-e", "--encrypt",
                                   action="store_true",
                                   required=False,
                                   help="Interactive mode for data encryption")
  interactive_options.add_argument("-d", "--decrypt",
                                   action="store_true",
                                   required=False,
                                   help="Interactive mode for data decryption")
  run_group.add_argument("-k", "--keyfile",
                         metavar="KEYFILE",
                         required=False,
                         help="The key filename to decrypt encrypted data (ignored in interactive mode)")
  run_group.add_argument("-w", "--workflow",
                         metavar="WORKFLOW",
                         nargs="+",
                         required=False,
                         help="Run the specified workflows sequentially")
  args = parser.parse_args()
  if args.encrypt or args.decrypt:
    interactive_mode(args)
  elif not args.workflow:
    laboro_help(parser)
  else:
    main(args.workflow, args.keyfile)
