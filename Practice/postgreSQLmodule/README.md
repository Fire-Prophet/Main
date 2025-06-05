# PostgreSQL Module

PostgreSQL 데이터베이스와의 연동, 데이터 처리, 분석, 내보내기를 위한 통합 모듈입니다.

## 🚀 주요 기능

### 1. 데이터베이스 관리 (`database.py`)
- PostgreSQL 연결 및 관리
- 쿼리 실행 및 트랜잭션 처리
- DataFrame과의 양방향 변환
- 테이블 정보 조회 및 백업

### 2. 데이터 처리 (`data_processor.py`)
- 데이터 정리 및 전처리
- 컬럼명 표준화
- 데이터 타입 변환
- 필터링, 집계, 피벗 등

### 3. 데이터 분석 (`analyzer.py`)
- 기술통계 분석
- 상관관계 분석
- 분포 및 이상치 분석
- 시계열 분석
- 가설 검정

### 4. 데이터 내보내기 (`exporter.py`)
- 다양한 형식 지원 (CSV, Excel, JSON, Parquet, HTML)
- 분석 리포트 생성
- 데이터 사전 생성

### 5. 통합 워크플로우 (`integration.py`)
- 모든 모듈을 통합한 완전 자동화 분석
- 테이블 비교 분석
- 사용자 정의 쿼리 분석

## 📦 설치

```bash
# 필수 패키지 설치
pip install -r requirements.txt
```

## 🔧 사용법

### 기본 사용법

```python
from postgreSQLmodule import PostgreSQLManager, DataProcessor, DataAnalyzer, DataExporter

# 1. 데이터베이스 연결
db = PostgreSQLManager(
    host="your_host",
    database="your_db", 
    user="your_user",
    password="your_password"
)

if db.connect():
    # 2. 데이터 로드
    df = db.to_dataframe("SELECT * FROM your_table")
    
    # 3. 데이터 처리
    processor = DataProcessor()
    cleaned_df = processor.clean_data(df)
    
    # 4. 데이터 분석
    analyzer = DataAnalyzer()
    stats = analyzer.descriptive_statistics(cleaned_df)
    
    # 5. 결과 내보내기
    exporter = DataExporter()
    exporter.to_csv(cleaned_df, "processed_data.csv")
    
    db.disconnect()
```

### 통합 클래스 사용 (권장)

```python
from postgreSQLmodule.integration import PostgreSQLIntegrator

# Context manager 사용
with PostgreSQLIntegrator() as integrator:
    # 테이블 완전 분석
    result = integrator.analyze_table("your_table")
    
    # 여러 테이블 비교
    comparison = integrator.compare_tables(["table1", "table2"])
    
    # 사용자 정의 분석
    custom = integrator.custom_analysis("SELECT * FROM custom_view")
```

## 📖 상세 예제

### 예제 1: 기본 데이터베이스 작업

```python
from postgreSQLmodule.database import PostgreSQLManager

db = PostgreSQLManager()
db.connect()

# 테이블 목록 조회
tables = db.get_tables()
print(f"테이블 수: {len(tables)}")

# 테이블 정보 조회
for table in tables[:3]:
    info = db.get_table_info(table)
    size = db.get_table_size(table)
    rows = db.get_row_count(table)
    
    print(f"\n{table}:")
    print(f"  컬럼 수: {len(info)}")
    print(f"  행 수: {rows:,}")
    print(f"  크기: {size.get('total_size', 'Unknown')}")

db.disconnect()
```

### 예제 2: 데이터 처리 파이프라인

```python
from postgreSQLmodule.data_processor import DataProcessor
import pandas as pd

# 샘플 데이터
df = pd.DataFrame({
    'User ID': range(1, 101),
    'User Name': [f'User {i}' for i in range(1, 101)],
    'Age': np.random.randint(18, 80, 100),
    'Income': np.random.normal(50000, 15000, 100)
})

processor = DataProcessor()

# 1. 컬럼명 표준화
df = processor.standardize_columns(df)

# 2. 데이터 정리
df = processor.clean_data(df, drop_duplicates=True)

# 3. 필터링
filters = {'age': {'min': 25, 'max': 65}}
df = processor.filter_data(df, filters)

# 4. 집계
aggregated = processor.aggregate_data(
    df, 
    'age_group', 
    {'income': ['mean', 'median', 'std']}
)
```

### 예제 3: 종합 분석

```python
from postgreSQLmodule.analyzer import DataAnalyzer

analyzer = DataAnalyzer()

# 기술통계
desc_stats = analyzer.descriptive_statistics(df)

# 상관관계
correlation = analyzer.correlation_analysis(df, threshold=0.3)

# 이상치 탐지
outliers = analyzer.outlier_analysis(df, methods=['iqr', 'zscore'])

# 인사이트 생성
insights = analyzer.generate_insights(df)

print("주요 인사이트:")
for insight in insights:
    print(f"- {insight}")
```

### 예제 4: 다양한 형식으로 내보내기

```python
from postgreSQLmodule.exporter import DataExporter

exporter = DataExporter("my_exports")

# 여러 형식으로 동시 내보내기
files = exporter.export_multiple_formats(
    df, 
    "analysis_results", 
    ['csv', 'excel', 'json', 'html']
)

# 분석 결과 리포트
analysis_results = {
    'descriptive': desc_stats,
    'correlation': correlation,
    'outliers': outliers
}

report_file = exporter.create_analysis_report(analysis_results)
print(f"분석 리포트: {report_file}")
```

## 🏗️ 모듈 구조

```
postgreSQLmodule/
├── __init__.py          # 패키지 초기화
├── database.py          # 데이터베이스 연결 및 관리
├── data_processor.py    # 데이터 처리 및 전처리
├── analyzer.py          # 데이터 분석 및 통계
├── exporter.py          # 데이터 내보내기
├── integration.py       # 통합 워크플로우
├── examples.py          # 사용 예제
├── requirements.txt     # 필수 패키지
└── README.md           # 이 파일
```

## 🔧 설정

### 환경 변수 설정 (선택사항)

```bash
export POSTGRES_PASSWORD="your_password"
export POSTGRES_HOST="your_host"
export POSTGRES_DB="your_database"
```

### 데이터베이스 연결 설정

```python
# 기본 설정
db_config = {
    'host': '123.212.210.230',
    'port': 5432,
    'user': 'postgres',
    'database': 'gis_db',
    'password': None  # 환경변수 또는 입력으로 받음
}

# 통합 클래스에 설정 전달
integrator = PostgreSQLIntegrator(db_config)
```

## 📊 지원하는 분석 유형

### 기술통계
- 평균, 중앙값, 최빈값
- 표준편차, 분산
- 사분위수, 범위
- 왜도, 첨도

### 고급 분석
- 피어슨/스피어만 상관관계
- 정규성 검정 (Shapiro-Wilk)
- 이상치 탐지 (IQR, Z-score)
- 시계열 분석 (추세, 계절성)
- 가설 검정 (t-test, ANOVA, Kruskal-Wallis)

### 데이터 품질 검사
- 결측값 분석
- 중복 데이터 탐지
- 데이터 타입 검증
- 카디널리티 분석

## 📁 내보내기 형식

- **CSV**: 범용 데이터 교환
- **Excel**: 비즈니스 리포팅 (다중 시트 지원)
- **JSON**: API 연동 및 웹 애플리케이션
- **Parquet**: 빅데이터 처리 (압축률 우수)
- **HTML**: 웹 기반 리포트 (시각적 테이블)

## 🔍 로깅

모든 모듈은 Python logging을 사용합니다:

```python
import logging

# 로깅 레벨 설정
logging.basicConfig(level=logging.INFO)

# 특정 모듈만 로깅
logger = logging.getLogger('postgreSQLmodule')
logger.setLevel(logging.DEBUG)
```

## 🚨 에러 처리

모든 함수는 안전한 에러 처리를 포함합니다:

- 데이터베이스 연결 실패 시 자동 재시도 없음 (명시적 처리)
- 잘못된 쿼리 시 빈 결과 반환
- 파일 저장 실패 시 빈 문자열 반환
- 모든 예외는 로그에 기록

## 🔗 의존성

### 핵심 패키지
- `psycopg2-binary`: PostgreSQL 연결
- `pandas`: 데이터 처리
- `numpy`: 수치 계산

### 분석 패키지
- `scipy`: 통계 분석
- `matplotlib`, `seaborn`: 시각화 지원

### 내보내기 패키지
- `openpyxl`: Excel 지원
- `pyarrow`: Parquet 지원

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 이슈를 생성해 주세요.

---

**주의사항**: 
- 이 모듈은 PostgreSQL 데이터베이스 연결이 필요합니다.
- 대용량 데이터 처리 시 메모리 사용량에 주의하세요.
- 분석 결과는 `exports/` 폴더에 저장됩니다.
