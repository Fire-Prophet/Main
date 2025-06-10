import os
def list_files(path):
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            list_files(full_path)
        else:
            print(full_path)

list_files(".")  # 현재 폴더 기준
