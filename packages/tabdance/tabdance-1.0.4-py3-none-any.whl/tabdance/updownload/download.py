import os

from tabdance.updownload.base import UpDownLoaderBase


class Downloader(UpDownLoaderBase):
  def __init__(self, args, config) -> None:
    super().__init__(args, config)

  def download(self) -> None:
    files = []
    files_in_remote_repo_path = self.ssh_connector.get_listdir(self.remote_repo_path)
    if self.args.file is not None:
      files = self.get_csv_meta_files_when_option_is_file(files_in_remote_repo_path, self.args.file)
    elif self.args.all:
      files = self.get_csv_meta_files_when_option_is_all(files_in_remote_repo_path)
    assert files != [], "No files to download"

    td_files = self.extract_td_files_from_files(files)
    files.extend(td_files)
    self.start_download_files(files)

  def extract_td_files_from_files(self, files) -> list:
    td_files = []
    for file in files:
      if file.endswith(".meta"):
        meta_file_path = f"{self.remote_repo_path}/{file}"
        td_file = self.ssh_connector.read_meta_file_and_return_td_file(meta_file_path)

        if td_file not in self.ssh_connector.get_listdir(self.remote_repo_path):
          raise Exception(f"No such file in {self.remote_repo_path}: {td_file}")
        if td_file not in td_files:
          td_files.append(td_file)

    return td_files

  def start_download_files(self, files) -> None:
    try:
      for file in files:
        local_path = os.path.join(self.local_repo_path, file)
        remote_path = f"{self.remote_repo_path}/{file}"
        print(file)
        self.ssh_connector.get_files(remote_path, local_path)
        print()
      print(f"Download Path: {self.local_repo_path}")
      print(f"Successfully Download: {files}")

    except Exception as e:
      raise Exception(f"Download Fail: {e}")
