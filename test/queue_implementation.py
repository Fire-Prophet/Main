from collections import deque

class Queue:
    """
    Python의 `collections.deque`를 사용하여 큐(Queue) 자료구조를 구현한 클래스입니다.
    큐는 FIFO(First-In, First-Out) 원칙을 따릅니다.
    주요 연산: enqueue (항목 추가), dequeue (항목 제거), front (맨 앞 항목 확인), is_empty (비어 있는지 확인), size (크기 확인).
    """
    def __init__(self):
        self._items = deque() # 큐의 요소를 저장할 deque 객체

    def enqueue(self, item):
        """
        큐의 뒤쪽에 항목을 추가합니다.
        시간 복잡도: O(1) - deque의 append 연산은 상수 시간입니다.
        """
        self._items.append(item)
        print(f"'{item}'을(를) 큐에 추가했습니다.")

    def dequeue(self):
        """
        큐의 맨 앞 항목을 제거하고 반환합니다.
        큐가 비어 있는 경우 IndexError를 발생시킵니다.
        시간 복잡도: O(1) - deque의 popleft 연산은 상수 시간입니다.
        """
        if self.is_empty():
            raise IndexError("큐가 비어 있습니다. dequeue할 수 없습니다.")
        dequeued_item = self._items.popleft()
        print(f"'{dequeued_item}'을(를) 큐에서 제거했습니다.")
        return dequeued_item

    def front(self):
        """
        큐의 맨 앞 항목을 제거하지 않고 반환합니다.
        큐가 비어 있는 경우 IndexError를 발생시킵니다.
        시간 복잡도: O(1)
        """
        if self.is_empty():
            raise IndexError("큐가 비어 있습니다. front 항목이 없습니다.")
        return self._items[0]

    def is_empty(self):
        """
        큐가 비어 있는지 여부를 확인합니다.
        시간 복잡도: O(1)
        """
        return len(self._items) == 0

    def size(self):
        """
        큐에 있는 항목의 수를 반환합니다.
        시간 복잡도: O(1)
        """
        return len(self._items)

    def display(self):
        """
        현재 큐의 모든 항목을 표시합니다.
        """
        if self.is_empty():
            print("큐가 비어 있습니다.")
        else:
            print("현재 큐 (앞쪽 -> 뒤쪽):")
            print(f"  {list(self._items)}") # deque를 리스트로 변환하여 출력
            print("--------------------")

if __name__ == "__main__":
    my_queue = Queue()

    print("--- 큐 초기화 ---")
    my_queue.display()

    print("\n--- 항목 추가 (enqueue) ---")
    my_queue.enqueue("Task A")
    my_queue.enqueue(123)
    my_queue.enqueue({"data": "example"})
    my_queue.display()

    print("\n큐 크기:", my_queue.size())
    print("큐가 비어 있나요?", my_queue.is_empty())
    print("맨 앞 항목 (front):", my_queue.front())

    print("\n--- 항목 제거 (dequeue) ---")
    print("제거된 항목:", my_queue.dequeue())
    my_queue.display()

    print("제거된 항목:", my_queue.dequeue())
    my_queue.display()

    print("\n큐가 비어 있나요?", my_queue.is_empty())

    print("\n--- 모든 항목 제거 ---")
    while not my_queue.is_empty():
        print("제거된 항목:", my_queue.dequeue())
    my_queue.display()

    print("\n--- 빈 큐에서 dequeue 시도 (예외 처리) ---")
    try:
        my_queue.dequeue()
    except IndexError as e:
        print(f"오류 발생: {e}")

    print("\n--- 빈 큐에서 front 시도 (예외 처리) ---")
    try:
        my_queue.front()
    except IndexError as e:
        print(f"오류 발생: {e}")
