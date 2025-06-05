// queries.js
console.log("📝 SQL 쿼리 모듈 로드됨.");

const { quotePgIdentifier } = require('./utils');
const {
    mysqlConnectionConfig, mysqlFuelDataTableName,
    forestTypeCodeCol, forestGeomCol, FOREST_GEOM_SRID_IN_DB,
    soilIdCol, soilTypeCodeCol, soilGeomCol, SOIL_GEOM_SRID_IN_DB
} = require('./config');

function getForestUnionQuery(forestTableFullNames) {
    const forestUnionQueryParts = forestTableFullNames.map(fullTableName => {
        const quotedForestTableName = quotePgIdentifier(fullTableName);
        return `SELECT "${forestTypeCodeCol}" AS frtp_cd, "${forestGeomCol}" AS geom, '${fullTableName}' AS source_forest_table FROM ${quotedForestTableName} WHERE ST_IsValid("${forestGeomCol}") AND ST_SRID("${forestGeomCol}") = ${FOREST_GEOM_SRID_IN_DB}`;
    });
    return `(${forestUnionQueryParts.join(' UNION ALL ')}) AS all_forest_data`;
}

function getSoilQuery(quotedSoilTableName) {
    return `
        SELECT
            "${soilIdCol}" AS soil_id,
            "${soilTypeCodeCol}" AS sltp_cd_val,
            ST_X(ST_Centroid("${soilGeomCol}")) AS x_output,
            ST_Y(ST_Centroid("${soilGeomCol}")) AS y_output,
            ST_Transform(ST_Centroid("${soilGeomCol}"), ${FOREST_GEOM_SRID_IN_DB}) AS centroid_for_join
        FROM ${quotedSoilTableName}
        WHERE "${soilGeomCol}" IS NOT NULL AND ST_IsValid("${soilGeomCol}") AND ST_SRID("${soilGeomCol}") = ${SOIL_GEOM_SRID_IN_DB};
    `;
}

function getSpatialQuery(forestUnionQuery) {
    return `
        SELECT frtp_cd, source_forest_table
        FROM ${forestUnionQuery}
        WHERE ST_Contains(geom, $1::geometry)
        LIMIT 1;
    `;
}

function getTruncateQuery() {
    return `TRUNCATE TABLE \`${mysqlConnectionConfig.database}\`.\`${mysqlFuelDataTableName}\`;`;
}

function getInsertQuery() {
    return `
        INSERT INTO \`${mysqlConnectionConfig.database}\`.\`${mysqlFuelDataTableName}\`
        (coord_x, coord_y, original_soil_id, soil_type_code, forest_type_code, soil_fuel_rating, forest_fuel_rating, total_fuel_strength, source_soil_table_name, source_forest_table_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    `;
}

module.exports = {
    getForestUnionQuery,
    getSoilQuery,
    getSpatialQuery,
    getTruncateQuery,
    getInsertQuery
};