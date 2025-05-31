# PostgreSQL Python 연결 모듈

이 폴더는 PostgreSQL 데이터베이스에 연결하고 기본적인 작업을 수행하기 위한 Python 모듈을 포함합니다.

## 파일 구조

- `db_connection.py`: PostgreSQL 연결을 위한 메인 클래스
- `example_usage.py`: 사용 예제 파일
- `requirements.txt`: 필요한 Python 패키지 목록
- `.env.template`: 환경변수 템플릿 파일

## 설치 및 설정

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정 (선택사항)

```bash
cp .env.template .env
# .env 파일을 편집하여 실제 비밀번호 입력
```

### 3. 직접 실행

```bash
python db_connection.py
```

## 데이터베이스 연결 정보

- **호스트**: 123.212.210.230
- **포트**: 5432
- **사용자**: postgres
- **데이터베이스**: gis_db
- **비밀번호**: 실행 시 입력 또는 환경변수 설정

## 사용법

### 기본 연결

```python
from db_connection import PostgreSQLConnection

# 데이터베이스 연결
db = PostgreSQLConnection()
if db.connect():
    # 쿼리 실행
    results = db.execute_query("SELECT * FROM your_table LIMIT 5")
    print(results)
    
    # 연결 종료
    db.disconnect()
```

### 환경변수 사용

```python
import os

# 환경변수에서 비밀번호 읽기
os.environ['POSTGRES_PASSWORD'] = 'your_password'

db = PostgreSQLConnection()
if db.connect():
    # 작업 수행
    pass
```

## 주요 기능

### PostgreSQLConnection 클래스

- `connect()`: 데이터베이스 연결
- `disconnect()`: 연결 종료
- `execute_query(query, params)`: SELECT 쿼리 실행
- `execute_command(command, params)`: INSERT/UPDATE/DELETE 실행
- `get_table_list()`: 테이블 목록 조회
- `get_table_info(table_name)`: 테이블 정보 조회
- `test_connection()`: 연결 테스트

### 사용 예제

```python
# 테이블 목록 조회
tables = db.get_table_list()
print("테이블 목록:", tables)

# 특정 테이블 정보 조회
if tables:
    table_info = db.get_table_info(tables[0])
    print("컬럼 정보:", table_info)

# 데이터 조회
results = db.execute_query("SELECT COUNT(*) as total FROM your_table")
print("총 레코드 수:", results[0]['total'])

# 데이터 삽입
success = db.execute_command(
    "INSERT INTO your_table (column1, column2) VALUES (%s, %s)",
    ("value1", "value2")
)
```

## PostGIS 지원

이 모듈은 PostGIS 확장이 설치된 데이터베이스에서 공간 데이터를 다루는 기능도 포함합니다.

```python
# PostGIS 설치 확인
result = db.execute_query("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')")

# 공간 테이블 조회
spatial_tables = db.execute_query("""
    SELECT f_table_name, f_geometry_column, type, srid 
    FROM geometry_columns
""")
```

## 에러 처리

모든 데이터베이스 작업은 적절한 에러 처리를 포함하고 있으며, 로깅을 통해 상세한 오류 정보를 제공합니다.

## 보안 주의사항

1. 비밀번호를 코드에 직접 하드코딩하지 마세요
2. 환경변수나 별도의 설정 파일을 사용하세요
3. `.env` 파일은 git에 커밋하지 마세요

## 라이센스

이 코드는 학습 및 개발 목적으로 자유롭게 사용할 수 있습니다.
