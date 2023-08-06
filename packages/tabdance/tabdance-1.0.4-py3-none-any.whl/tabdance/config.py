import os

from configparser import ConfigParser
from pathlib import Path


class TableDataSyncConfig:
  def __init__(self) -> None:
    self.tabdance_directory_path = os.path.join(os.path.expanduser("~"), ".tabdance/")
    self.config_file_path = os.path.join(self.tabdance_directory_path, "tabdance.cfg")

  def create_config_file(self) -> None:
    self.create_tabdance_directory_if_not_exists()
    if self.is_exists_config_file():
      print("Already created tabdance.cfg file")
    else:
      config = self.read_default_config_for_inital_setup()
      with open(self.config_file_path, "w") as config_file:
        config.write(config_file)

  def create_tabdance_directory_if_not_exists(self) -> None:
    if not os.path.exists(self.tabdance_directory_path):
      os.mkdir(self.tabdance_directory_path)

  def is_exists_config_file(self) -> bool:
    if os.path.exists(self.config_file_path):
      return True
    return False

  def read_default_config_for_inital_setup(self) -> ConfigParser:
    default_config_path = Path(__file__).resolve().parent.joinpath("tabdance.default.cfg")
    default_config = ConfigParser()
    default_config.read(default_config_path)
    return default_config

  def check_config(func):
    def decorate(*args, **kwargs):
      self = args[0]
      assert os.path.exists(self.config_file_path), "Not exists config file, First create and set a config file"
      return func(*args, **kwargs)
    return decorate

  @check_config
  def get_config(self) -> ConfigParser:
    config = ConfigParser()
    config.read(self.config_file_path)
    return config

  @check_config
  def print_config(self) -> None:
    config = self.get_config()
    for section in config.sections():
      for option in config.options(section):
        print(f"{section}.{option}={config[section][option]}")

  @check_config
  def set_config(self, section, option, value) -> None:
    config = self.get_config()
    config.set(section.upper(), option.lower(), value)
    with open(self.config_file_path, "w") as config_file:
      config.write(config_file)

  def assert_error_if_not_exists_config_info_for_updownload(self) -> None:
    config = self.get_config()
    assert config.get("PATH", "local_repo_path") != "", "path.local_repo_path is empty"
    assert config.get("PATH", "remote_repo_path") != "", "path.remote_repo_path is empty"
    assert config.get("REMOTE_INFO", "remote_host_name") != "", "remote_info.remote_host_name is empty"
    assert config.get("REMOTE_INFO", "remote_user_name") != "", "remote_info.remote_user_name is empty"
    assert config.get("REMOTE_INFO", "remote_user_password") != "", "remote_info.remote_user_password is empty"

  def assert_error_if_not_exists_config_info_for_update(self) -> None:
    config = self.get_config()
    assert config.get("PATH", "local_repo_path") != "", "path.local_repo_path is empty"
    assert config.get("DB", "sqlalchemy_database_uri") != "", "db.sqlalchemy_database_uri is empty"
    assert config.get("DB", "schema") != "", "db.schema is empty"
    assert config.get("DB", "table") != "", "db.table is empty"
