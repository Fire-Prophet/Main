require('dotenv').config(); // .env 파일 로드
const mysql = require('mysql2/promise');

// MySQL 연결 설정 (환경 변수에서 로드)
const mysqlConnectionConfig = {
    host: process.env.MYSQL_HOST,
    user: process.env.MYSQL_USER,
    password: process.env.MYSQL_PASSWORD,
    database: process.env.MYSQL_DATABASE,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
};

// 원본 데이터 테이블 (상세 연료 데이터)
const SOURCE_FUEL_TABLE = 'fuel_data_asan_cheonan';

// 대상 테이블 (산불 예측 시뮬레이션용 포인트 데이터)
const TARGET_PREDICT_TABLE = 'fire_predict_points';

async function populatePredictPointsTable() {
    let connection;
    console.log(`--- '${TARGET_PREDICT_TABLE}' 테이블 데이터 채우기 스크립트 시작 ---`);

    try {
        // MySQL 연결
        connection = await mysql.createConnection(mysqlConnectionConfig);
        console.log("MySQL 연결 성공!");

        // 1. 대상 테이블 비우기
        console.log(`'${TARGET_PREDICT_TABLE}' 테이블 비우기 (TRUNCATE) 시도...`);
        await connection.execute(`TRUNCATE TABLE \`${TARGET_PREDICT_TABLE}\``);
        console.log(`'${TARGET_PREDICT_TABLE}' 테이블 비우기 완료.`);

        // 2. 원본 테이블에서 데이터 복사
        const insertQuery = `
            INSERT INTO \`${TARGET_PREDICT_TABLE}\` (id, coord_x, coord_y, total_fuel_strength)
            SELECT id, coord_x, coord_y, total_fuel_strength 
            FROM \`${SOURCE_FUEL_TABLE}\`;
        `;
        console.log(`'${SOURCE_FUEL_TABLE}' 테이블에서 '${TARGET_PREDICT_TABLE}' 테이블로 데이터 복사 시도...`);
        const [result] = await connection.execute(insertQuery);
        console.log(`데이터 복사 완료. 총 ${result.affectedRows}개의 행이 '${TARGET_PREDICT_TABLE}' 테이블에 삽입되었습니다.`);

        console.log(`--- '${TARGET_PREDICT_TABLE}' 테이블 데이터 채우기 성공 ---`);

    } catch (error) {
        console.error(`!!! '${TARGET_PREDICT_TABLE}' 테이블 데이터 채우기 중 오류 발생:`, error);
    } finally {
        if (connection) {
            await connection.end();
            console.log("MySQL 연결 종료됨.");
        }
        console.log(`--- 스크립트 종료 ---`);
    }
}

// 스크립트 실행
populatePredictPointsTable();