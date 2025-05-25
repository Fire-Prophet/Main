const admin = require('firebase-admin');

const SERVICE_ACCOUNT_PATH = './serviceAccountKey.json';
const FIREBASE_DATABASE_URL = 'https://ljg2020315018-default-rtdb.firebaseio.com';

let db;

function initializeFirebase() {
    if (!db) {
        try {
            const serviceAccount = require(SERVICE_ACCOUNT_PATH);
            admin.initializeApp({
                credential: admin.credential.cert(serviceAccount),
                databaseURL: FIREBASE_DATABASE_URL,
            });
            db = admin.database();
            console.log("Firebase 초기화 성공.");
        } catch (error) {
            console.error("Firebase 초기화 실패:", error.message);
            process.exit(1);
        }
    }
    return db;
}

module.exports = initializeFirebase;
