# simple_queue.py
import collections
import threading
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleQueue:
    def __init__(self, max_size=0):
        """
        간단한 스레드 안전 큐를 초기화합니다.
        max_size: 큐의 최대 크기 (0이면 무제한).
        """
        self.queue = collections.deque()
        self.max_size = max_size
        self.lock = threading.Lock() # 큐 접근을 위한 락
        self.not_empty = threading.Condition(self.lock) # 큐가 비어있지 않음을 알림
        self.not_full = threading.Condition(self.lock)  # 큐가 가득 차지 않았음을 알림
        logging.info(f"SimpleQueue initialized with max_size={max_size}.")

    def put(self, item):
        """
        큐에 항목을 추가합니다. 큐가 가득 차면 대기합니다.
        """
        with self.not_full:
            while self.max_size > 0 and len(self.queue) >= self.max_size:
                logging.info(f"Queue is full ({len(self.queue)}/{self.max_size}). Waiting to put item.")
                self.not_full.wait()
            self.queue.append(item)
            logging.info(f"Item '{item}' put into queue. Current size: {len(self.queue)}")
            self.not_empty.notify() # 큐에 항목이 추가되었음을 알림

    def get(self):
        """
        큐에서 항목을 가져옵니다. 큐가 비어 있으면 대기합니다.
        """
        with self.not_empty:
            while not self.queue:
                logging.info("Queue is empty. Waiting to get item.")
                self.not_empty.wait()
            item = self.queue.popleft()
            logging.info(f"Item '{item}' got from queue. Current size: {len(self.queue)}")
            self.not_full.notify() # 큐에 공간이 생겼음을 알림
            return item

    def qsize(self):
        """
        큐의 현재 크기를 반환합니다.
        """
        with self.lock:
            return len(self.queue)

    def is_empty(self):
        """
        큐가 비어있는지 확인합니다.
        """
        with self.lock:
            return not bool(self.queue)

    def is_full(self):
        """
        큐가 가득 찼는지 확인합니다.
        """
        with self.lock:
            return self.max_size > 0 and len(self.queue) >= self.max_size

# 예시 사용
if __name__ == "__main__":
    my_queue = SimpleQueue(max_size=3)

    def producer():
        for i in range(5):
            time.sleep(0.1) # 생산 지연
            my_queue.put(f"item-{i}")

    def consumer():
        for i in range(5):
            time.sleep(0.5) # 소비 지연
            item = my_queue.get()
            print(f"Consumed: {item}, Queue size: {my_queue.qsize()}")

    producer_thread = threading.Thread(target=producer)
    consumer_thread = threading.Thread(target=consumer)

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()
    print("All tasks finished.")
