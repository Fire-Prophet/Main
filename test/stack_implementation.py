class Stack:
    """
    Python 리스트를 사용하여 스택(Stack) 자료구조를 구현한 클래스입니다.
    스택은 LIFO(Last-In, First-Out) 원칙을 따릅니다.
    주요 연산: push (항목 추가), pop (항목 제거), peek (가장 위 항목 확인), is_empty (비어 있는지 확인), size (크기 확인).
    """
    def __init__(self):
        self._items = [] # 스택의 요소를 저장할 비공개 리스트

    def push(self, item):
        """
        스택의 맨 위에 항목을 추가합니다.
        시간 복잡도: O(1) - 리스트의 append 연산은 보통 상수 시간입니다.
        """
        self._items.append(item)
        print(f"'{item}'을(를) 스택에 푸시했습니다.")

    def pop(self):
        """
        스택의 맨 위 항목을 제거하고 반환합니다.
        스택이 비어 있는 경우 IndexError를 발생시킵니다.
        시간 복잡도: O(1) - 리스트의 pop() 연산은 보통 상수 시간입니다.
        """
        if self.is_empty():
            raise IndexError("스택이 비어 있습니다. pop할 수 없습니다.")
        popped_item = self._items.pop()
        print(f"'{popped_item}'을(를) 스택에서 팝했습니다.")
        return popped_item

    def peek(self):
        """
        스택의 맨 위 항목을 제거하지 않고 반환합니다.
        스택이 비어 있는 경우 IndexError를 발생시킵니다.
        시간 복잡도: O(1)
        """
        if self.is_empty():
            raise IndexError("스택이 비어 있습니다. peek할 항목이 없습니다.")
        return self._items[-1]

    def is_empty(self):
        """
        스택이 비어 있는지 여부를 확인합니다.
        시간 복잡도: O(1)
        """
        return len(self._items) == 0

    def size(self):
        """
        스택에 있는 항목의 수를 반환합니다.
        시간 복잡도: O(1)
        """
        return len(self._items)

    def display(self):
        """
        현재 스택의 모든 항목을 표시합니다.
        """
        if self.is_empty():
            print("스택이 비어 있습니다.")
        else:
            # 스택의 맨 위가 리스트의 끝에 해당하므로, 역순으로 출력하여 스택 시각화
            print("현재 스택 (상단 -> 하단):")
            for item in reversed(self._items):
                print(f"  {item}")
            print("--------------------")


if __name__ == "__main__":
    my_stack = Stack()

    print("--- 스택 초기화 ---")
    my_stack.display()

    print("\n--- 항목 푸시 ---")
    my_stack.push(10)
    my_stack.push("Hello")
    my_stack.push(True)
    my_stack.display()

    print("\n스택 크기:", my_stack.size())
    print("스택이 비어 있나요?", my_stack.is_empty())
    print("맨 위 항목 (peek):", my_stack.peek())

    print("\n--- 항목 팝 ---")
    print("팝된 항목:", my_stack.pop())
    my_stack.display()

    print("팝된 항목:", my_stack.pop())
    my_stack.display()

    print("\n스택이 비어 있나요?", my_stack.is_empty())

    print("\n--- 모든 항목 팝 ---")
    while not my_stack.is_empty():
        print("팝된 항목:", my_stack.pop())
    my_stack.display()

    print("\n--- 빈 스택에서 팝 시도 (예외 처리) ---")
    try:
        my_stack.pop()
    except IndexError as e:
        print(f"오류 발생: {e}")

    print("\n--- 빈 스택에서 peek 시도 (예외 처리) ---")
    try:
        my_stack.peek()
    except IndexError as e:
        print(f"오류 발생: {e}")
