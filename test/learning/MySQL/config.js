// config.js
require('dotenv').config(); // .env 파일 로드 (반드시 가장 먼저 호출!)
console.log("📜 설정 파일 로드됨 (.env 사용).");

// --- ⚙️ 데이터베이스 연결 정보 (from .env) ---
const pgConfig = {
    user: process.env.PG_USER, // .env 파일의 PG_USER 값 사용
    host: process.env.PG_HOST,
    database: process.env.PG_DATABASE,
    password: process.env.PG_PASSWORD, // .env 파일의 PG_PASSWORD 값 사용
    port: parseInt(process.env.PG_PORT, 10) || 5432 // 기본값 설정 및 정수 변환
};

const mysqlConnectionConfig = {
    host: process.env.MYSQL_HOST,
    port: parseInt(process.env.MYSQL_PORT, 10) || 3306,
    user: process.env.MYSQL_USER,
    password: process.env.MYSQL_PASSWORD,
    database: process.env.MYSQL_DATABASE
};

// .env 변수가 제대로 로드되었는지 확인 (중요!)
if (!pgConfig.user || !pgConfig.password || !mysqlConnectionConfig.user || !mysqlConnectionConfig.password) {
    console.error("❌ 오류: .env 파일에 필수 데이터베이스 정보(USER, PASSWORD)가 설정되지 않았습니다. 스크립트를 종료합니다.");
    process.exit(1); // 필수 정보 없으면 스크립트 종료
}


// --- 🔥 MySQL 테이블 이름 ---
const mysqlFuelDataTableName = 'fuel_data_asan_cheonan';

// --- 🌲 대상 테이블, 컬럼, 좌표계(SRID) 정보 (이전과 동일) ---
const SOIL_GEOM_SRID_IN_DB = 4326;
const FOREST_GEOM_SRID_IN_DB = 5179;
const soilTableFullNames = [ 'public.Asan_Cheonan_Soil_1', 'public.Asan_Cheonan_Soil_2', 'public.Asan_Cheonan_Soil_3' ];
const soilIdCol = 'id';
const soilGeomCol = 'geom';
const soilTypeCodeCol = 'SLTP_CD';
const forestTableFullNames = [ 'public.imsangdo_part1', 'public.imsangdo_part2', 'public.imsangdo_part3' ];
const forestTypeCodeCol = 'FRTP_CD';
const forestGeomCol = 'geom';

module.exports = {
    pgConfig,
    mysqlConnectionConfig,
    mysqlFuelDataTableName,
    SOIL_GEOM_SRID_IN_DB,
    FOREST_GEOM_SRID_IN_DB,
    soilTableFullNames,
    soilIdCol,
    soilGeomCol,
    soilTypeCodeCol,
    forestTableFullNames,
    forestTypeCodeCol,
    forestGeomCol
};