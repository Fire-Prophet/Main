# db_connector.py
import sqlite3
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DBConnector:
    def __init__(self, db_name="my_database.db"):
        """
        SQLite 데이터베이스 연결 클래스 초기화.
        """
        self.db_name = db_name
        self.conn = None
        logging.info(f"DBConnector initialized for database: {db_name}")

    def connect(self):
        """
        데이터베이스에 연결합니다.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row # 결과를 딕셔너리처럼 접근 가능하게 설정
            logging.info(f"Successfully connected to database: {self.db_name}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database {self.db_name}: {e}")
            return False

    def disconnect(self):
        """
        데이터베이스 연결을 닫습니다.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            logging.info(f"Disconnected from database: {self.db_name}")
            return True
        logging.warning("Attempted to disconnect, but no active connection found.")
        return False

    def execute_query(self, query, params=()):
        """
        데이터베이스 쿼리를 실행하고 결과를 반환합니다 (SELECT).
        """
        if not self.conn:
            logging.error("No active database connection. Call connect() first.")
            return None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            logging.info(f"Query executed successfully: {query[:50]}...")
            return rows
        except sqlite3.Error as e:
            logging.error(f"Error executing query '{query[:50]}...': {e}")
            return None

    def execute_non_query(self, query, params=()):
        """
        데이터베이스 쿼리를 실행하고 변경된 행 수를 반환합니다 (INSERT, UPDATE, DELETE).
        """
        if not self.conn:
            logging.error("No active database connection. Call connect() first.")
            return -1
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            logging.info(f"Non-query executed successfully: {query[:50]}... Rows affected: {cursor.rowcount}")
            return cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"Error executing non-query '{query[:50]}...': {e}")
            self.conn.rollback() # 오류 발생 시 롤백
            return -1

# 예시 사용
if __name__ == "__main__":
    db = DBConnector("example.db")

    if db.connect():
        # 테이블 생성
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER
        );
        """
        db.execute_non_query(create_table_sql)

        # 데이터 삽입
        db.execute_non_query("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 30))
        db.execute_non_query("INSERT INTO users (name, age) VALUES (?, ?)", ("Bob", 25))

        # 데이터 조회
        users = db.execute_query("SELECT * FROM users")
        if users:
            print("\nUsers in DB:")
            for user in users:
                print(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")

        # 데이터 업데이트
        db.execute_non_query("UPDATE users SET age = ? WHERE name = ?", (31, "Alice"))

        # 업데이트된 데이터 조회
        updated_users = db.execute_query("SELECT * FROM users WHERE name = ?", ("Alice",))
        if updated_users:
            print("\nUpdated Alice:")
            for user in updated_users:
                print(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")

        db.disconnect()

    # 생성된 DB 파일 삭제 (선택 사항)
    # import os
    # if os.path.exists("example.db"):
    #     os.remove("example.db")
    #     logging.info("Cleaned up example.db")
