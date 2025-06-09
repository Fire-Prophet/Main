import os
import shutil

folder = input("정리할 폴더 경로를 입력하세요: ")

for file in os.listdir(folder):
    file_path = os.path.join(folder, file)
    if os.path.isfile(file_path):
        ext = file.split(".")[-1]
        ext_folder = os.path.join(folder, ext)
        os.makedirs(ext_folder, exist_ok=True)
        shutil.move(file_path, os.path.join(ext_folder, file))

print("📁 파일 정리가 완료되었습니다!")
