// main.js
console.log("--- 아산/천안 연료 데이터 생성 스크립트 (모듈화 버전) ---");

const { getPgConnection, getMysqlConnection } = require('./db');
const { soilTableFullNames, forestTableFullNames } = require('./config');
const { soilFuelRatings, forestFuelRatings } = require('./ratings');
const { getForestUnionQuery, getSoilQuery, getSpatialQuery, getTruncateQuery, getInsertQuery } = require('./queries');
const { quotePgIdentifier, getCurrentTime } = require('./utils');

console.log("현재 시간:", getCurrentTime());

async function generateFuelData() {
    let pgClient, pgPool, mysqlConn;
    let totalProcessedSoilRecords = 0, totalInsertedToMysql = 0, totalErrorsEncountered = 0, totalSpatialQueryNotFound = 0;

    try {
        ({ pool: pgPool, client: pgClient } = await getPgConnection());
        mysqlConn = await getMysqlConnection();

        await mysqlConn.execute(getTruncateQuery());
        console.log(`MySQL 테이블 비우기 완료 (초기화).`);

        const forestUnionQuery = getForestUnionQuery(forestTableFullNames);
        console.log("임상도 통합 쿼리 부분 생성 완료.");
        const spatialQuery = getSpatialQuery(forestUnionQuery);

        for (const fullSoilTableName of soilTableFullNames) {
            const quotedSoilTableName = quotePgIdentifier(fullSoilTableName);
            console.log(`\n[토양 테이블 처리 시작] '${quotedSoilTableName}'`);

            const soilQuery = getSoilQuery(quotedSoilTableName);
            const soilResult = await pgClient.query(soilQuery);
            console.log(`'${quotedSoilTableName}'에서 ${soilResult.rowCount}개 레코드 조회 준비 완료.`);

            let tableProcessedCount = 0;
            for (const soilRow of soilResult.rows) {
                totalProcessedSoilRecords++;
                tableProcessedCount++;

                if (tableProcessedCount % 100 === 0 || tableProcessedCount === soilResult.rowCount) {
                    console.log(`  '${quotedSoilTableName}' 테이블: ${tableProcessedCount} / ${soilResult.rowCount} 처리 중...`);
                }

                if (soilRow.x_output == null || soilRow.y_output == null || !isFinite(soilRow.x_output) || !isFinite(soilRow.y_output)) {
                    console.warn(`  [경고] soil_id '${soilRow.soil_id}' 좌표 계산 실패. 건너뜁니다.`);
                    totalErrorsEncountered++;
                    continue;
                }

                let frtp_cd_value = null;
                let matchedForestTable = null;

                try {
                    const forestResult = await pgClient.query(spatialQuery, [soilRow.centroid_for_join]);
                    if (forestResult.rows.length > 0) {
                        frtp_cd_value = forestResult.rows[0].frtp_cd;
                        matchedForestTable = forestResult.rows[0].source_forest_table;
                    } else {
                        totalSpatialQueryNotFound++;
                    }
                } catch (spatialErr) {
                    console.error(`  [오류] soil_id '${soilRow.soil_id}' 공간 쿼리 실패:`, spatialErr.message);
                    totalErrorsEncountered++;
                }

                const currentSltpCd = soilRow.sltp_cd_val ? String(soilRow.sltp_cd_val).trim() : null;
                const currentFrtpCd = frtp_cd_value ? String(frtp_cd_value).trim() : null;

                const soilRating = soilFuelRatings[currentSltpCd] || soilFuelRatings['DEFAULT'];
                const forestRating = forestFuelRatings[currentFrtpCd] || forestFuelRatings['DEFAULT'];
                const totalFuelStrength = soilRating + forestRating;

                const valuesForInsert = [
                    soilRow.x_output, soilRow.y_output,
                    soilRow.soil_id ? String(soilRow.soil_id) : null,
                    currentSltpCd, currentFrtpCd,
                    soilRating, forestRating, totalFuelStrength,
                    fullSoilTableName, matchedForestTable
                ];

                if (valuesForInsert.some(val => val === undefined)) {
                    console.error(`  [오류] undefined 값이 포함되어 삽입 불가 (soil_id: '${soilRow.soil_id}'). 건너뜁니다.`);
                    totalErrorsEncountered++;
                    continue;
                }

                try {
                    await mysqlConn.execute(getInsertQuery(), valuesForInsert);
                    totalInsertedToMysql++;
                } catch (mysqlErr) {
                    console.error(`  [오류] MySQL 저장 실패 (soil_id: '${soilRow.soil_id}'):`, mysqlErr.message);
                    totalErrorsEncountered++;
                }
            }
            console.log(`'${quotedSoilTableName}' 테이블 처리 완료.`);
        }

        console.log("\n--- 모든 데이터 처리 완료 ---");
        console.log(`총 처리된 토양 레코드 수: ${totalProcessedSoilRecords}`);
        console.log(`MySQL에 성공적으로 저장된 레코드 수: ${totalInsertedToMysql}`);
        console.log(`임상도 정보 못 찾은 경우: ${totalSpatialQueryNotFound}`);
        console.log(`오류 또는 건너뛴 레코드 수: ${totalErrorsEncountered}`);

    } catch (error) {
        console.error("!!! 스크립트 실행 중 예외 발생:", error);
    } finally {
        if (pgClient) { pgClient.release(); console.log("PostGIS 클라이언트 연결 반환됨."); }
        if (pgPool) { await pgPool.end(); console.log("PostGIS 연결 풀 종료됨."); }
        if (mysqlConn) { await mysqlConn.end(); console.log("MySQL 연결 종료됨."); }
        console.log("--- 스크립트 종료 ---");
    }
}

generateFuelData();