// db.js
console.log("💾 데이터베이스 연결 모듈 로드됨.");

const { Pool: PgPool } = require('pg');
const mysql = require('mysql2/promise');
const { pgConfig, mysqlConnectionConfig } = require('./config');

async function getPgConnection() {
    const pool = new PgPool(pgConfig);
    const client = await pool.connect();
    console.log("PostGIS 연결 성공!");
    return { pool, client };
}

async function getMysqlConnection() {
    const connection = await mysql.createConnection(mysqlConnectionConfig);
    console.log("MySQL 연결 성공!");
    return connection;
}

module.exports = {
    getPgConnection,
    getMysqlConnection
};