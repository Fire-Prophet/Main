# PostgreSQL Python 연결 및 분석 도구

이 폴더는 PostgreSQL 데이터베이스에 연결하고 테이블 분석, 데이터 품질 검사, 데이터 내보내기 등의 종합적인 데이터베이스 관리 작업을 수행하기 위한 Python 모듈을 포함합니다.

## 파일 구조

### 핵심 모듈
- `db_connection.py`: PostgreSQL 연결을 위한 메인 클래스
- `table_analyzer.py`: 테이블 상세 분석 도구
- `data_quality_checker.py`: 데이터 품질 검사 도구
- `data_exporter.py`: 다양한 형식으로 데이터 내보내기 도구
- `comprehensive_analyzer.py`: 모든 기능을 통합한 메인 인터페이스

### 예제 및 설정
- `example_usage.py`: 기본 사용 예제 파일
- `requirements.txt`: 필요한 Python 패키지 목록
- `.env.template`: 환경변수 템플릿 파일

### 생성되는 디렉토리
- `exports/`: 내보낸 파일들이 저장되는 디렉토리 (자동 생성)

## 주요 기능

### 🔍 테이블 상세 분석
- 테이블 기본 정보 (크기, 레코드 수, 소유자 등)
- 컬럼 상세 정보 (데이터 타입, NULL 여부, 기본값 등)
- 인덱스 정보 및 사용 통계
- 제약조건 정보
- 공간 데이터 정보 (PostGIS)
- 테이블 활동 통계

### 🔍 데이터 품질 검사
- **NULL 값 검사**: 각 컬럼의 NULL 비율 분석
- **중복 값 검사**: 데이터 고유성 검사
- **데이터 일관성 검사**: 숫자 컬럼의 이상치 탐지
- **참조 무결성 검사**: 외래키 제약조건 위반 검사
- **종합 품질 점수**: 전체적인 데이터 품질 평가

### 📁 데이터 내보내기
- **CSV 형식**: 표준 CSV 파일로 내보내기
- **JSON 형식**: JSON 파일로 내보내기
- **GeoJSON 형식**: 공간 데이터를 GeoJSON으로 내보내기
- **분석 보고서**: 테이블 분석 결과를 텍스트/JSON 보고서로 저장

### 📊 데이터베이스 모니터링
- 데이터베이스 기본 정보
- 설치된 확장 기능 목록
- 테이블별 활동 통계
- 인덱스 사용 통계
- 연결 상태 모니터링

### 🌍 공간 데이터 분석
- 공간 테이블 목록
- 공간 범위 (bounding box) 계산
- 기하 통계 (면적, 둘레 등)
- 좌표계 정보

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

### 3. 실행 방법

#### 종합 분석 도구 실행 (권장)
```bash
python comprehensive_analyzer.py
```

#### 개별 모듈 실행
```bash
# 테이블 상세 분석
python table_analyzer.py

# 데이터 품질 검사
python data_quality_checker.py

# 데이터 내보내기
python data_exporter.py

# 기본 연결 테스트
python db_connection.py
```

## 데이터베이스 연결 정보

- **호스트**: 123.212.210.230
- **포트**: 5432
- **사용자**: postgres
- **데이터베이스**: gis_db
- **비밀번호**: 실행 시 입력 또는 환경변수 설정

## 사용법

### 🚀 빠른 시작 (종합 분석 도구)

```bash
python comprehensive_analyzer.py
```

메뉴에서 원하는 기능을 선택하여 사용:
1. 📊 테이블 상세 분석
2. 🔍 데이터 품질 검사  
3. 📁 데이터 내보내기
4. 📋 데이터베이스 정보
5. 🔄 공간 데이터 분석
6. 📈 성능 모니터링

### 💻 프로그래밍 방식 사용

#### 기본 연결

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

#### 테이블 상세 분석

```python
from table_analyzer import PostgreSQLTableAnalyzer

analyzer = PostgreSQLTableAnalyzer()
if analyzer.connect():
    # 특정 테이블 종합 분석
    analyzer.analyze_table_comprehensive('your_table_name')
    analyzer.disconnect()
```

#### 데이터 품질 검사

```python
from data_quality_checker import PostgreSQLDataQualityChecker

checker = PostgreSQLDataQualityChecker()
if checker.connect():
    # 데이터 품질 종합 검사
    results = checker.comprehensive_quality_check('your_table_name')
    checker.print_quality_report(results)
    checker.disconnect()
```

#### 데이터 내보내기

```python
from data_exporter import PostgreSQLDataExporter

exporter = PostgreSQLDataExporter()
if exporter.connect():
    # CSV로 내보내기
    exporter.export_table_to_csv('your_table_name', limit=1000)
    
    # JSON으로 내보내기
    exporter.export_table_to_json('your_table_name', limit=1000)
    
    # 공간 데이터를 GeoJSON으로 내보내기
    exporter.export_spatial_data_to_geojson('spatial_table', 'geom_column')
    exporter.disconnect()
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

## 주요 기능 상세

### 🔍 PostgreSQLConnection 클래스

- `connect()`: 데이터베이스 연결
- `disconnect()`: 연결 종료
- `execute_query(query, params)`: SELECT 쿼리 실행
- `execute_command(command, params)`: INSERT/UPDATE/DELETE 실행
- `get_table_list()`: 테이블 목록 조회
- `get_table_info(table_name)`: 테이블 정보 조회
- `test_connection()`: 연결 테스트

### 📊 PostgreSQLTableAnalyzer 클래스

- `get_all_tables()`: 모든 테이블 기본 정보 조회
- `get_table_columns_detailed(table_name)`: 컬럼 상세 정보
- `get_table_indexes(table_name)`: 인덱스 정보 및 사용 통계
- `get_table_constraints(table_name)`: 제약조건 정보
- `get_spatial_info(table_name)`: 공간 데이터 정보
- `get_spatial_extent(table_name, geom_column)`: 공간 범위 계산
- `analyze_table_comprehensive(table_name)`: 종합 테이블 분석

### 🔍 PostgreSQLDataQualityChecker 클래스

- `check_null_values(table_name)`: NULL 값 검사
- `check_duplicate_values(table_name)`: 중복 값 검사
- `check_data_consistency(table_name)`: 데이터 일관성 검사
- `check_referential_integrity(table_name)`: 참조 무결성 검사
- `comprehensive_quality_check(table_name)`: 종합 품질 검사
- `print_quality_report(results)`: 품질 보고서 출력

### 📁 PostgreSQLDataExporter 클래스

- `export_table_to_csv(table_name, limit, where_clause)`: CSV 내보내기
- `export_table_to_json(table_name, limit, where_clause)`: JSON 내보내기
- `export_spatial_data_to_geojson(table_name, geom_column, limit)`: GeoJSON 내보내기
- `export_analysis_report(table_name, analysis_data)`: 분석 보고서 저장
- `get_export_summary()`: 내보내기 요약 정보

## 사용 예제

### 기본 테이블 조회

```python
# 테이블 목록 조회
db = PostgreSQLConnection()
if db.connect():
    tables = db.get_table_list()
    print("테이블 목록:", tables)
    
    # 특정 테이블 정보
    table_info = db.get_table_info('your_table_name')
    print("테이블 정보:", table_info)
    
    db.disconnect()
```

### 공간 데이터 조회

```python
# PostGIS 공간 데이터 쿼리
spatial_query = """
SELECT 
    ST_AsText(geom) as geometry_text,
    ST_Area(geom) as area,
    * 
FROM spatial_table 
LIMIT 5
"""

results = db.execute_query(spatial_query)
for row in results:
    print(f"면적: {row['area']}, 기하: {row['geometry_text'][:50]}...")
```

### 고급 분석 예제

```python
from comprehensive_analyzer import PostgreSQLComprehensiveAnalyzer

# 종합 분석기 사용
analyzer = PostgreSQLComprehensiveAnalyzer()
analyzer.run()  # 대화형 메뉴 실행
```

## 출력 파일

### 분석 보고서 (exports/ 디렉토리)
- `{table_name}_analysis_{timestamp}.txt`: 텍스트 분석 보고서
- `{table_name}_analysis_{timestamp}.json`: JSON 분석 보고서
- `{table_name}_quality_{timestamp}.txt`: 데이터 품질 보고서

### 데이터 내보내기
- `{table_name}_{timestamp}.csv`: CSV 데이터 파일
- `{table_name}_{timestamp}.json`: JSON 데이터 파일
- `{table_name}_{timestamp}.geojson`: GeoJSON 공간 데이터 파일

## 주요 특징

### ✅ 장점
- 종합적인 데이터베이스 분석 기능
- PostGIS 공간 데이터 지원
- 다양한 내보내기 형식 지원
- 데이터 품질 평가 및 등급 제공
- 사용자 친화적인 대화형 인터페이스
- 자동 파일 저장 및 관리

### 🔧 요구사항
- Python 3.7+
- PostgreSQL 9.6+
- PostGIS 2.4+ (공간 데이터 기능 사용 시)

### 📊 지원하는 데이터 타입
- 모든 PostgreSQL 기본 데이터 타입
- 공간 데이터 타입 (geometry, geography)
- JSON/JSONB 데이터
- 배열 데이터 타입

## 문제 해결

### 연결 오류
```bash
# 방화벽 확인
telnet 123.212.210.230 5432

# PostgreSQL 서비스 상태 확인
pg_isready -h 123.212.210.230 -p 5432
```

### 권한 오류
- 데이터베이스 사용자에게 적절한 권한이 있는지 확인
- 특히 `pg_stat_user_tables`, `information_schema` 접근 권한 필요

### 메모리 오류
- 대용량 테이블 내보내기 시 `limit` 파라미터 사용
- WHERE 조건으로 데이터 필터링

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

버그 리포트, 기능 요청, 풀 리퀘스트를 환영합니다.

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
