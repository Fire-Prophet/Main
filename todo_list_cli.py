# todo_list_cli.py
import json
import os

TODO_FILE = "mytodos.json"

def load_todos():
    """JSON 파일에서 할 일 목록을 불러옵니다."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return [] # 파일이 비어있거나 형식이 잘못된 경우
    return []

def save_todos(todos):
    """할 일 목록을 JSON 파일에 저장합니다."""
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=4)

def add_todo(todos, task):
    """새로운 할 일을 목록에 추가합니다."""
    todos.append({"task": task, "completed": False})
    print(f"'{task}' 할 일이 추가되었습니다.")

def view_todos(todos):
    """할 일 목록을 보여줍니다."""
    if not todos:
        print("할 일이 없습니다!")
        return
    print("\n--- 나의 할 일 ---")
    for idx, todo in enumerate(todos):
        status = "✓" if todo["completed"] else "✗"
        print(f"{idx + 1}. [{status}] {todo['task']}")
    print("------------------")

def mark_complete(todos, task_number):
    """지정된 번호의 할 일을 완료 처리합니다."""
    try:
        task_idx = int(task_number) - 1
        if 0 <= task_idx < len(todos):
            todos[task_idx]["completed"] = True
            print(f"'{todos[task_idx]['task']}' 완료 처리되었습니다.")
        else:
            print("잘못된 할 일 번호입니다.")
    except ValueError:
        print("숫자를 입력해주세요.")

def remove_todo(todos, task_number):
    """지정된 번호의 할 일을 삭제합니다."""
    try:
        task_idx = int(task_number) - 1
        if 0 <= task_idx < len(todos):
            removed_task = todos.pop(task_idx)
            print(f"'{removed_task['task']}' 할 일이 삭제되었습니다.")
        else:
            print("잘못된 할 일 번호입니다.")
    except ValueError:
        print("숫자를 입력해주세요.")


def main():
    """할 일 목록 앱 메인 함수"""
    todos = load_todos()

    while True:
        print("\n어떤 작업을 하시겠습니까?")
        print("1. 할 일 추가")
        print("2. 할 일 보기")
        print("3. 할 일 완료 표시")
        print("4. 할 일 삭제")
        print("5. 종료")
        
        choice = input("선택: ")

        if choice == '1':
            task = input("추가할 할 일을 입력하세요: ")
            add_todo(todos, task)
            save_todos(todos)
        elif choice == '2':
            view_todos(todos)
        elif choice == '3':
            view_todos(todos)
            task_num = input("완료 처리할 할 일 번호를 입력하세요: ")
            mark_complete(todos, task_num)
            save_todos(todos)
        elif choice == '4':
            view_todos(todos)
            task_num = input("삭제할 할 일 번호를 입력하세요: ")
            remove_todo(todos, task_num)
            save_todos(todos)
        elif choice == '5':
            print("할 일 목록 앱을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main()
