import json
import paramiko

from tabdance.base import callback_progressbar


class SSHConnector:
  def __init__(self, config) -> None:
    self.config = config
    self.ssh_client = None
    self.sftp = None

  def connect_sftp(self) -> None:
    self.ssh_client = paramiko.SSHClient()
    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh_client.connect(
        hostname=self.config["REMOTE_INFO"]["REMOTE_HOST_NAME"],
        username=self.config["REMOTE_INFO"]["REMOTE_USER_NAME"],
        password=self.config["REMOTE_INFO"]["REMOTE_USER_PASSWORD"]
    )
    self.sftp = self.ssh_client.open_sftp()

  def check_sftp(func):
    def decorate(*args, **kwargs):
      self = args[0]
      assert self.sftp is not None, "SSH is not connect, sftp is none"
      return func(*args, **kwargs)
    return decorate

  @check_sftp
  def disconnect_sftp(self) -> None:
    self.sftp.close()
    self.ssh_client.close()

  @check_sftp
  def get_files(self, remote_path, local_path) -> None:
    self.sftp.get(remote_path, local_path, callback=callback_progressbar)

  @check_sftp
  def put_files(self, local_path, remote_path) -> None:
    self.sftp.put(local_path, remote_path, callback=callback_progressbar)

  @check_sftp
  def get_listdir(self, path) -> list:
    return self.sftp.listdir(path)

  @check_sftp
  def read_meta_file_and_return_td_file(self, meta_file_path) -> str:
    with self.sftp.open(meta_file_path, "r") as meta_file:
      td_file = json.load(meta_file)["table_name"] + ".td"
    return td_file
