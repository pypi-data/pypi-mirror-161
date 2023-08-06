from tabdance.command import CommandParser
from tabdance.config import TableDataSyncConfig
from tabdance.update import DBTableBase, DBTableSync
from tabdance.updownload.download import Downloader
from tabdance.updownload.upload import Uploader


def main():
  args = CommandParser().get_args()
  if args.command == "config":
    run_tabdance_config(args)
  elif args.command == "download":
    run_tabdance_download(args)
  elif args.command == "upload":
    run_tabdance_upload(args)
  elif args.command == "update":
    run_tabdance_update()


def run_tabdance_config(args):
  tabdance_config = TableDataSyncConfig()
  if args.create:
    tabdance_config.create_config_file()
  elif args.list:
    tabdance_config.print_config()
  elif args.update:
    section = args.update[0].split(".")[0]
    option = args.update[0].split(".")[1]
    value = args.update[1]
    tabdance_config.set_config(section, option, value)


def run_tabdance_download(args):
  tabdance_config = TableDataSyncConfig()
  tabdance_config.assert_error_if_not_exists_config_info_for_updownload()
  config = tabdance_config.get_config()

  downloader = Downloader(args, config)
  downloader.ssh_connector.connect_sftp()
  downloader.download()
  downloader.ssh_connector.disconnect_sftp()


def run_tabdance_upload(args):
  tabdance_config = TableDataSyncConfig()
  tabdance_config.assert_error_if_not_exists_config_info_for_updownload()
  config = tabdance_config.get_config()

  uploader = Uploader(args, config)
  uploader.ssh_connector.connect_sftp()
  uploader.upload()
  uploader.ssh_connector.disconnect_sftp()


def run_tabdance_update():
  tabdance_config = TableDataSyncConfig()
  tabdance_config.assert_error_if_not_exists_config_info_for_update()
  config = tabdance_config.get_config()
  DBTableBase(config).init_db_object()
  DBTableSync(config).sync_table()
