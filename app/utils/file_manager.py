from pathlib import Path

ENC = "utf-8"


def check_file_exist(file_path: str) -> bool:
    try:
        my_file = Path(file_path)
        return my_file.is_file()
    except OSError:
        return False


def read_file(file_path, encoding=ENC):
    if check_file_exist(file_path=file_path):
        try:
            f = open(file_path, "r", encoding=encoding)
            print(f.read())
            f.close()
        except OSError as e:
            print(f"ERROR: {e}")
    else:
        print("File not found!")


def write_file(file_path):
    if check_file_exist(file_path=file_path):
        try:
            f = open(file_path, "a", encoding=ENC)
            f.write("Now the file has more content!")
            f.close()
        except OSError as e:
            print(f"ERROR: {e}")
    else:
        try:
            f = open("myfile.txt", "w", encoding=ENC)
        except OSError as oe:
            print(f"ERROR: {oe}")
