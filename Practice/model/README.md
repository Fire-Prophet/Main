2. 데이터 수집 및 전처리
	1.	지형·연료·토양 데이터 불러오기
	•	GeoTIFF나 Shapefile 형태의 지형고도·연료맵을 Rasterio/GeoPandas로 로드
	2.	실시간 기상 API 연동
	•	MetPy 또는 Siphon 등으로 온도·습도·풍속 데이터 수집 스크립트 작성
	3.	데이터 정합성 체크
	•	좌표계統일 (PyProj), 결측치 처리, 해상도 리샘플링
	4.	EDA(탐색적 분석)
	•	Matplotlib/Seaborn으로 주요 변수 분포와 상관관계 시각화