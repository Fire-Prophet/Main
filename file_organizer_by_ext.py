# file_organizer_by_ext.py
import os
import shutil

def organize_files_by_extension(source_directory):
    """
    주어진 디렉토리의 파일들을 확장자별로 하위 폴더를 만들어 정리합니다.
    """
    if not os.path.isdir(source_directory):
        print(f"오류: '{source_directory}'는 유효한 디렉토리가 아닙니다.")
        return

    print(f"'{source_directory}' 디렉토리의 파일을 정리합니다...")

    for filename in os.listdir(source_directory):
        source_file_path = os.path.join(source_directory, filename)

        if os.path.isfile(source_file_path):
            # 파일 확장자 가져오기 (예: .txt, .jpg)
            # 숨김 파일 ('.DS_Store' 등)은 건너뛸 수 있도록 수정
            if '.' not in filename or filename.startswith('.'):
                print(f"건너뜀 (확장자 없거나 숨김 파일): {filename}")
                continue
            
            file_extension = filename.split('.')[-1].lower()
            if not file_extension: # 확장자가 없는 경우 (예: 'myfile.')
                print(f"건너뜀 (확장자 없음): {filename}")
                continue

            # 확장자 이름으로 대상 폴더 경로 생성
            destination_folder_path = os.path.join(source_directory, file_extension)

            # 대상 폴더가 없으면 생성
            if not os.path.exists(destination_folder_path):
                try:
                    os.makedirs(destination_folder_path)
                    print(f"폴더 생성됨: {destination_folder_path}")
                except OSError as e:
                    print(f"폴더 생성 실패 '{destination_folder_path}': {e}")
                    continue
            
            # 파일 이동
            destination_file_path = os.path.join(destination_folder_path, filename)
            try:
                shutil.move(source_file_path, destination_file_path)
                print(f"이동: {filename} -> {file_extension}/{filename}")
            except Exception as e:
                print(f"파일 이동 실패 '{filename}': {e}")
        else:
            print(f"건너뜀 (디렉토리): {filename}")
            
    print("파일 정리가 완료되었습니다.")

def main():
    """메인 함수: 사용자로부터 대상 디렉토리를 입력받음"""
    target_dir = input("정리할 디렉토리 경로를 입력하세요 (예: ./my_downloads): ")
    if not target_dir:
        print("경로가 입력되지 않았습니다. 현재 디렉토리의 'organize_target' 폴더를 생성하여 테스트합니다.")
        target_dir = "organize_target"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        # 테스트용 파일 생성
        with open(os.path.join(target_dir, "test.txt"), "w") as f: f.write("hello")
        with open(os.path.join(target_dir, "image.jpg"), "w") as f: f.write("data")
        with open(os.path.join(target_dir, "document.pdf"), "w") as f: f.write("data")
        with open(os.path.join(target_dir, "archive.zip"), "w") as f: f.write("data")
        with open(os.path.join(target_dir, "no_ext_file"), "w") as f: f.write("data")


    organize_files_by_extension(target_dir)

if __name__ == "__main__":
    main()
