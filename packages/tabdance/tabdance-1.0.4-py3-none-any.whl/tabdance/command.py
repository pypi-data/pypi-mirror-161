import argparse


class CommandParser:
  def __init__(self) -> None:
    self.parser = argparse.ArgumentParser(prog="tabdance")
    self.subparsers = self.parser.add_subparsers(dest="command", help="Table Data Sync Operation")

  def get_args(self) -> argparse.Namespace:
    self.add_updownload_command()
    self.add_update_command()
    self.add_config_command()
    return self.parser.parse_args()

  def add_updownload_command(self) -> None:
    for load_type in ["upload", "download"]:
      if load_type == "upload":
        help_comment = f"Upload data from LOCAL_REPO_PATH to REMOTE_REPO_PATH"
      else:
        help_comment = f"Download data from REMOTE_REPO_PATH to LOCAL_REPO_PATH"

      load_parser = self.subparsers.add_parser(load_type, help=help_comment)
      options_group = load_parser.add_mutually_exclusive_group(required=True)
      options_group.add_argument("-f", "--file", nargs="+", help=f"Write file name you want to {load_type}")
      options_group.add_argument("-a", "--all", action="store_true", help=f"All file {load_type}")

  def add_update_command(self) -> None:
    self.subparsers.add_parser("update", help="Compare and update the DB table with csv of LOCAL_REPO_PATH")

  def add_config_command(self) -> None:
    config_parser = self.subparsers.add_parser("config", help="tabdance config file create, read, update")
    options_group = config_parser.add_mutually_exclusive_group(required=True)
    options_group.add_argument("--create", action="store_true", help="Create '~/.tabdance/tabdance.cfg' file")
    options_group.add_argument("--list", action="store_true", help="Show tabdance config information")
    options_group.add_argument("--update", nargs=2, help="Setting tabdance config file, ex) Section.Option Information")
