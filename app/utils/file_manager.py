from pathlib import Path

def check_file_exist(file_path: str) -> bool:
  try:
    my_file = Path(file_path)
    return my_file.is_file()
  except Exception as e:
    return False


def read_file(file_path, encoding = 'utf-8'):
  if check_file_exist(file_path= file_path):
    try:  
        f = open(file_path, "r", encoding=encoding)
        print(f.read())
        f.close()
    except Exception as e:
      print(f"ERROR: {e}")
  else:
    print("File not found!")


def writeFile(file_path):
  if check_file_exist(file_path=file_path):
    try:
      f = open(file_path, "a")
      f.write("Now the file has more content!")
      f.close()
    except Exception as e:
      print(F"ERROR: {e}")
  else:
    try:
      f = open("myfile.txt", "w")
    except Exception as e:
      print(F"ERROR: {e}")