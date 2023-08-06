import math
import sys


def convert_size(file_size) -> str:
  """file size 변환"""
  if file_size == 0:
      return "0B"
  byte_unit = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
  index = int(math.log(file_size, 1024))
  byte_size = math.pow(1024, index)
  size = round(file_size / byte_size, 2)
  return f"{size} {byte_unit[index]}"


def callback_progressbar(size, total_size) -> None:
  """진행바 출력"""
  bar_len = 100
  filled_len = math.ceil(bar_len * size / float(total_size))
  percent = math.ceil(100.0 * size / float(total_size))
  bar = "#" * filled_len + " " * (bar_len - filled_len)
  file_size = convert_size(total_size)
  sys.stdout.write(f"\r\t|{bar}| {percent}% {file_size}")
