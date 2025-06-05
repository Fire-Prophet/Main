# contact_book_cli.py
import json
import os

CONTACTS_FILE = "contacts.json"

def load_contacts():
    """JSON 파일에서 연락처를 불러옵니다."""
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # 파일이 비어있거나 형식이 잘못된 경우
    return {}

def save_contacts(contacts):
    """연락처를 JSON 파일에 저장합니다."""
    with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=4)

def add_contact(contacts):
    """새로운 연락처를 추가합니다."""
    name = input("이름: ")
    if name in contacts:
        print(f"'{name}'은(는) 이미 연락처에 존재합니다.")
        return
    phone = input("전화번호: ")
    email = input("이메일 (선택사항): ")
    contacts[name] = {"phone": phone, "email": email if email else None}
    print(f"'{name}' 연락처가 추가되었습니다.")

def view_contacts(contacts):
    """모든 연락처를 보여줍니다."""
    if not contacts:
        print("연락처가 비어있습니다.")
        return
    print("\n--- 연락처 목록 ---")
    for name, info in contacts.items():
        print(f"이름: {name}, 전화번호: {info['phone']}", end="")
        if info['email']:
            print(f", 이메일: {info['email']}")
        else:
            print()
    print("--------------------")

def search_contact(contacts):
    """이름으로 연락처를 검색합니다."""
    name_to_search = input("검색할 이름을 입력하세요: ")
    if name_to_search in contacts:
        info = contacts[name_to_search]
        print(f"\n--- 검색 결과 ---")
        print(f"이름: {name_to_search}")
        print(f"전화번호: {info['phone']}")
        if info['email']:
            print(f"이메일: {info['email']}")
        print("-----------------")
    else:
        print(f"'{name_to_search}'을(를) 찾을 수 없습니다.")

def delete_contact(contacts):
    """연락처를 삭제합니다."""
    name_to_delete = input("삭제할 연락처의 이름을 입력하세요: ")
    if name_to_delete in contacts:
        del contacts[name_to_delete]
        print(f"'{name_to_delete}' 연락처가 삭제되었습니다.")
    else:
        print(f"'{name_to_delete}'을(를) 찾을 수 없습니다.")

def main():
    """연락처 관리 프로그램 메인 함수"""
    contacts_data = load_contacts()

    while True:
        print("\n연락처 관리 프로그램")
        print("1. 연락처 추가")
        print("2. 연락처 보기")
        print("3. 연락처 검색")
        print("4. 연락처 삭제")
        print("5. 종료")
        
        choice = input("선택: ")

        if choice == '1':
            add_contact(contacts_data)
            save_contacts(contacts_data)
        elif choice == '2':
            view_contacts(contacts_data)
        elif choice == '3':
            search_contact(contacts_data)
        elif choice == '4':
            delete_contact(contacts_data)
            save_contacts(contacts_data)
        elif choice == '5':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main()
