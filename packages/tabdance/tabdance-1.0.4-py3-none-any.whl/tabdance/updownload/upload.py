import json
import os

from csv import reader

from tabdance.updownload.base import UpDownLoaderBase


class Uploader(UpDownLoaderBase):
  def __init__(self, args, config) -> None:
    super().__init__(args, config)

  def upload(self) -> None:
    files = []
    files_in_local_repo_path = os.listdir(self.local_repo_path)
    if self.args.file is not None:
      files = self.get_csv_meta_files_when_option_is_file(files_in_local_repo_path, self.args.file)
    elif self.args.all:
      files = self.get_csv_meta_files_when_option_is_all(files_in_local_repo_path)
    assert files != [], "No files to upload"

    td_files = self.extract_td_files_from_files(files)
    files.extend(td_files)

    self.check_column_match_in_meta_file(files)
    self.start_upload_files(files)

  def extract_td_files_from_files(self, files) -> list:
    td_files = []
    for file in files:
      if file.endswith(".meta"):
        meta_file_path = os.path.join(self.local_repo_path, file)
        td_file = self.read_meta_file_and_return_td_file(meta_file_path)

        if td_file not in os.listdir(self.local_repo_path):
          raise Exception(f"No such file in {self.local_repo_path}: {td_file}")
        if td_file not in td_files:
          td_files.append(td_file)

    return td_files

  def read_meta_file_and_return_td_file(self, meta_file_path) -> str:
    with open(meta_file_path, "r") as meta_file:
      td_file = json.load(meta_file)["table_name"] + ".td"
    return td_file

  def check_column_match_in_meta_file(self, files) -> None:
    try:
      meta_files = [file for file in files if file.endswith(".meta")]
      for meta_file in meta_files:
        with open(os.path.join(self.local_repo_path, meta_file), "r") as f_meta:
          meta_datas = json.load(f_meta)
          if "column_match" in meta_datas.keys():
            self.check_exist_csv_header(meta_file, meta_datas)
            self.check_exist_td_column(meta_datas)

    except AssertionError as e:
      raise Exception(e)

  def check_exist_td_column(self, meta_datas) -> None:
    td_file = f"{meta_datas['table_name']}.td"
    with open(os.path.join(self.local_repo_path, td_file), "r") as f_td:
      table_schema = json.load(f_td)
      columns = [column["name"] for column in table_schema["columns"]]

    for value in meta_datas["column_match"].values():
      assert value in columns, f"Not exists '{value}' in .td file"

  def check_exist_csv_header(self, meta_file, meta_datas) -> None:
    csv_file = f"{os.path.splitext(meta_file)[0]}.csv"
    with open(os.path.join(self.local_repo_path, csv_file), "r") as f_csv:
      csv_reader = reader(f_csv)
      headers = next(csv_reader)

    for key in meta_datas["column_match"].keys():
      assert key in headers, f"Not exists '{key}' in csv file headers"

  def start_upload_files(self, files) -> None:
    try:
      for file in files:
        local_path = os.path.join(self.local_repo_path, file)
        remote_path = f"{self.remote_repo_path}/{file}"
        print(file)
        self.ssh_connector.put_files(local_path, remote_path)
        print()
      print(f"Successfully Upload: {files}")

    except Exception as e:
      raise Exception(f"Upload Fail: {e}")
