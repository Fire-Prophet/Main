-- simple_db_operations.sql

-- 데이터베이스 생성 (이미 존재한다면 건너뛰기)
-- 이 명령어는 데이터베이스 클라이언트에서 실행해야 합니다.
-- CREATE DATABASE my_sample_db;
-- \c my_sample_db; -- 데이터베이스 연결 (psql에서)

-- 1. 'products' 테이블 생성
-- 제품 정보를 저장하기 위한 테이블을 정의합니다.
-- 제품 ID는 기본 키이며, 이름은 고유해야 합니다.
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,    -- 제품 고유 ID (자동 증가)
    product_name VARCHAR(100) UNIQUE NOT NULL, -- 제품 이름 (고유하고 NULL 허용 안 함)
    price DECIMAL(10, 2) NOT NULL,    -- 제품 가격 (소수점 2자리까지)
    stock_quantity INT NOT NULL DEFAULT 0, -- 재고 수량 (기본값 0)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- 레코드 생성 시간
);

-- 인덱스 추가 (선택 사항이지만 검색 성능 향상에 도움)
CREATE INDEX IF NOT EXISTS idx_product_name ON products (product_name);

-- 2. 'products' 테이블에 데이터 삽입
-- 새로운 제품 레코드를 테이블에 추가합니다.
INSERT INTO products (product_name, price, stock_quantity) VALUES
('노트북', 1200.00, 50),
('무선 마우스', 25.50, 200),
('기계식 키보드', 80.00, 75),
('USB 허브', 15.75, 150);

-- 이미 존재하는 제품 이름을 삽입하려고 시도하면 오류가 발생합니다.
-- INSERT INTO products (product_name, price, stock_quantity) VALUES ('노트북', 1300.00, 30); -- UNIQUE 제약 조건 위반

-- 3. 'products' 테이블의 모든 데이터 조회
-- 테이블에 저장된 모든 제품 정보를 가져옵니다.
SELECT
    product_id,
    product_name,
    price,
    stock_quantity,
    created_at
FROM
    products;

-- 4. 특정 조건으로 데이터 조회 (예: 가격이 50보다 큰 제품)
SELECT
    product_name,
    price
FROM
    products
WHERE
    price > 50.00
ORDER BY
    price DESC; -- 가격이 높은 순서대로 정렬

-- 5. 데이터 업데이트 (예: '노트북'의 재고 수량 변경)
UPDATE
    products
SET
    stock_quantity = 45,
    price = 1150.00
WHERE
    product_name = '노트북';

-- 업데이트 후 해당 제품만 다시 조회하여 변경 확인
SELECT
    product_name,
    price,
    stock_quantity
FROM
    products
WHERE
    product_name = '노트북';

-- 6. 데이터 삭제 (예: 'USB 허브' 제품 삭제)
DELETE FROM
    products
WHERE
    product_name = 'USB 허브';

-- 삭제 후 모든 데이터 다시 조회하여 확인
SELECT * FROM products;

-- 7. 테이블 삭제 (정리용, 필요시 주석 해제)
-- DROP TABLE IF EXISTS products;
