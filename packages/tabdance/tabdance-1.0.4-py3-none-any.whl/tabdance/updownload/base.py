from tabdance.updownload.ssh import SSHConnector


class UpDownLoaderBase:
  def __init__(self, args, config) -> None:
    self.args = args
    self.local_repo_path = config["PATH"]["LOCAL_REPO_PATH"]
    self.remote_repo_path = config["PATH"]["REMOTE_REPO_PATH"]
    self.ssh_connector = SSHConnector(config)

  def get_csv_meta_files_when_option_is_file(self, files_in_repo_path, files_input_by_user) -> list:
    files = []
    for file in files_input_by_user:
      csv_file = f"{file}.csv"
      meta_file = f"{file}.meta"

      if self.is_exists_file_in_file_list(csv_file, files_in_repo_path):
        files.append(csv_file)
      if self.is_exists_file_in_file_list(meta_file, files_in_repo_path):
        files.append(meta_file)

    return files

  def get_csv_meta_files_when_option_is_all(self, files_in_repo_path) -> list:
    files = []
    include_extensions = (".csv", ".meta")
    for file in files_in_repo_path:
      if file.endswith(include_extensions):
        files.append(file)
    return files

  def is_exists_file_in_file_list(self, file, file_list) -> bool:
    if file in file_list:
      return True
    raise Exception(f"No such file: {file}")
