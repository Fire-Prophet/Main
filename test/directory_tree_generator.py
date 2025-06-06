# directory_tree_generator.py
import os

def generate_directory_tree(start_path, indent_char='|   ', max_depth=None, current_depth=0):
    """
    주어진 경로로부터 디렉토리 트리를 생성하여 문자열로 반환합니다.
    :param start_path: 트리를 시작할 디렉토리 경로
    :param indent_char: 들여쓰기에 사용할 문자
    :param max_depth: 탐색할 최대 깊이 (None이면 무제한)
    :param current_depth: 현재 탐색 깊이 (내부 재귀용)
    :return: 디렉토리 트리 문자열
    """
    if not os.path.isdir(start_path):
        return f"오류: '{start_path}'는 유효한 디렉토리가 아닙니다."

    tree_output = []
    # 현재 디렉토리 이름 추가 (루트 디렉토리의 경우)
    if current_depth == 0:
        tree_output.append(os.path.basename(os.path.abspath(start_path)))

    # 최대 깊이 도달 시 중단
    if max_depth is not None and current_depth >= max_depth:
        return "\n".join(tree_output)

    try:
        # 디렉토리 내 항목들을 정렬하여 일관된 순서로 표시
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        tree_output.append(f"{indent_char * current_depth}{indent_char}└── [접근 권한 없음]")
        return "\n".join(tree_output)


    for i, entry_name in enumerate(entries):
        entry_path = os.path.join(start_path, entry_name)
        is_last_entry = (i == len(entries) - 1)
        
        prefix = indent_char * current_depth
        connector = '└── ' if is_last_entry else '├── '
        
        tree_output.append(f"{prefix}{connector}{entry_name}")
        
        if os.path.isdir(entry_path):
            # 재귀적으로 하위 디렉토리 탐색
            # 다음 깊이로 넘어갈 때, is_last_entry에 따라 indent_char 수정
            next_indent = indent_char * (current_depth + 1)
            if not is_last_entry : # 현재 항목이 마지막이 아니면, 다음 들여쓰기에도 | 유지
                 # 이 부분은 복잡해질 수 있어, 간단하게 indent_char를 그대로 넘김
                 # 좀 더 정확한 트리 모양을 위해서는 복잡한 로직이 필요할 수 있음
                 pass


            sub_tree = generate_directory_tree(entry_path, indent_char, max_depth, current_depth + 1)
            # sub_tree의 각 라인에 적절한 prefix 추가
            sub_tree_lines = sub_tree.splitlines()
            # 첫 번째 라인(하위 디렉토리 이름 자체)은 이미 위에서 추가했으므로 제외하고
            # 나머지 하위 트리 구조를 추가.
            # 이 예제에서는 generate_directory_tree가 전체 경로를 반환하지 않고
            # 현재 깊이부터의 트리만 반환하도록 하여, 위에서 connector와 함께 entry_name을 출력하고
            # 재귀 호출은 그 하위 내용만 가져오도록 함.
            # 따라서, 아래 코드는 약간의 수정이 필요함.
            # 위에서 print(f"{prefix}{connector}{entry_name}") 로 이미 출력했으므로,
            # 재귀 호출은 그 하위 항목만 가져와야 함.
            # 여기서는 generate_directory_tree가 해당 entry_path의 *내용*을 반환한다고 가정.

            # generate_directory_tree를 수정하여, 각 라인 앞에 붙일 prefix를 인자로 받거나,
            # 반환값을 후처리하는 방식이 필요.
            # 현재 구조에서는, 하위 디렉토리의 이름을 재귀 호출 시 다시 출력하지 않도록 수정해야 함.
            
            # 간단한 해결: 재귀호출에서 반환된 문자열의 첫 줄(디렉토리명)은 제외하고 추가
            # 또는 재귀호출 시, 현재 디렉토리명을 출력하지 않도록 수정.
            # 이 예제에서는 generate_directory_tree 함수가 좀 더 복잡해지지 않도록
            # 현재 깊이의 항목들을 직접 출력하고, 하위 디렉토리에 대해서만 재귀호출하는 방식을 유지.
            # (위의 tree_output.append(f"{prefix}{connector}{entry_name}")가 그 역할)
            # 따라서, 아래 코드는 추가적인 prefix 조정이 필요할 수 있다.
            # 여기서는 재귀 호출 결과 문자열들을 그대로 이어붙이는 것으로 단순화.
            # (실제로는 각 줄에 맞는 prefix가 붙어야 함)

            # 현재 버전은 최상위 디렉토리 이름만 먼저 출력하고,
            # 그 다음부터는 재귀적으로 파일/디렉토리 이름을 prefix와 함께 추가하는 방식
            if os.path.isdir(entry_path): # 재확인
                # 재귀 호출 시, depth를 증가시키고, 반환된 문자열을 결과에 추가
                # 이 방식은 sub_tree의 각 라인에 prefix를 다시 붙여야 함.
                # 아래는 generate_directory_tree가 하위 항목 리스트를 반환한다고 가정하고 재구성
                # 여기서는 일단 현재 구조를 유지하며, 하위 디렉토리의 내용을 가져와 붙임.
                # (개선 필요 지점)
                pass # 위에서 이미 처리됨.

    # 위 루프에서 tree_output에 하위 항목들이 추가됨.
    # generate_directory_tree가 호출될 때마다, 그 경로의 하위 항목들을 tree_output에 추가하는 방식.
    # 루트 호출 시, 시작 경로의 이름만 먼저 넣고, 그 후 내부 항목들을 처리.
    # 재귀 호출 시에는, 해당 하위 디렉토리의 항목들을 처리.

    # 이 구조에서는 main 함수에서 첫 호출 시 prefix를 다르게 처리하거나,
    # generate_directory_tree 함수 내부에서 depth 0일 때만 특별 처리하는 것이 좋음.
    # 현재는 depth 0일 때 basename을 추가하고, 그 후 loop에서 하위 항목을 처리.
    # 재귀 호출에서는 해당 경로의 항목들만 처리하고 반환.
    
    # 최종적으로 완성된 tree_output을 문자열로 합쳐 반환
    return "\n".join(tree_output)


# generate_directory_tree 함수를 좀 더 직관적으로 수정
def generate_tree_recursive(current_path, prefix="", is_last_sibling=False, max_depth=None, current_depth=0):
    """재귀적으로 디렉토리 트리를 생성하는 헬퍼 함수"""
    output_lines = []
    
    if max_depth is not None and current_depth > max_depth:
        return []

    try:
        entries = sorted(os.listdir(current_path))
    except PermissionError:
        return [f"{prefix}└── [접근 권한 없음]"]
    except FileNotFoundError: # 심볼릭 링크가 깨진 경우 등
        return [f"{prefix}└── [경로 없음 또는 접근 불가]"]


    for i, name in enumerate(entries):
        is_last = (i == len(entries) - 1)
        entry_path = os.path.join(current_path, name)
        
        # 현재 항목에 대한 줄 생성
        connector = "└── " if is_last else "├── "
        output_lines.append(f"{prefix}{connector}{name}")
        
        if os.path.isdir(entry_path) and not os.path.islink(entry_path): # 심볼릭 링크 디렉토리는 재귀 안함
            # 다음 재귀를 위한 prefix 생성
            # 현재가 마지막 자식이면 다음 prefix는 공백, 아니면 | 추가
            new_prefix = prefix + ("    " if is_last else "|   ")
            sub_tree_lines = generate_tree_recursive(entry_path, new_prefix, is_last, max_depth, current_depth + 1)
            output_lines.extend(sub_tree_lines)
            
    return output_lines


def get_directory_tree_string(start_path, max_depth_str=None):
    """디렉토리 트리 문자열을 생성하는 메인 인터페이스 함수"""
    if not os.path.isdir(start_path):
        return f"오류: '{start_path}'는 유효한 디렉토리가 아닙니다."

    actual_max_depth = None
    if max_depth_str:
        try:
            actual_max_depth = int(max_depth_str)
            if actual_max_depth < 0:
                print("최대 깊이는 0 이상이어야 합니다. 제한 없이 탐색합니다.")
                actual_max_depth = None
        except ValueError:
            print("잘못된 최대 깊이 값입니다. 제한 없이 탐색합니다.")
            actual_max_depth = None

    tree_lines = [os.path.basename(os.path.abspath(start_path))] # 루트 디렉토리 이름
    tree_lines.extend(generate_tree_recursive(start_path, "", True, actual_max_depth, 0))
    return "\n".join(tree_lines)


def main():
    """디렉토리 트리 생성기 메인 함수"""
    print("디렉토리 트리 생성기입니다.")
    target_dir = input("트리를 생성할 디렉토리 경로를 입력하세요 (기본값: 현재 디렉토리): ")
    if not target_dir:
        target_dir = "." # 현재 디렉토리
    
    max_depth_input = input("최대 탐색 깊이를 입력하세요 (숫자, 빈칸은 무제한): ")

    # 테스트를 위한 임시 디렉토리 및 파일 생성
    if target_dir == "." and not os.path.exists("sample_dir_for_tree"):
        os.makedirs("sample_dir_for_tree/subdir1/subsubdir1", exist_ok=True)
        os.makedirs("sample_dir_for_tree/subdir2", exist_ok=True)
        with open("sample_dir_for_tree/file1.txt", "w") as f: f.write("f1")
        with open("sample_dir_for_tree/subdir1/file2.txt", "w") as f: f.write("f2")
        with open("sample_dir_for_tree/subdir1/subsubdir1/file3.txt", "w") as f: f.write("f3")
        with open("sample_dir_for_tree/subdir2/file4.log", "w") as f: f.write("f4")
        print(f"\n참고: 테스트를 위해 '{os.path.abspath('sample_dir_for_tree')}'에 샘플 구조를 생성했습니다.")
        print(f"해당 경로로 테스트해보세요: sample_dir_for_tree")


    print("\n--- 디렉토리 트리 ---")
    tree_structure = get_directory_tree_string(target_dir, max_depth_input)
    print(tree_structure)
    print("--------------------")

if __name__ == "__main__":
    main()
