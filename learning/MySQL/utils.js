// utils.js
console.log("🛠️ 유틸리티 모듈 로드됨.");

function quotePgIdentifier(fullName) {
    const parts = fullName.split('.');
    if (parts.length === 2) { return `"${parts[0]}"."${parts[1]}"`; }
    return `"${fullName}"`;
}

function getCurrentTime() {
    return new Date().toLocaleString("ko-KR", { timeZone: "Asia/Seoul" });
}

module.exports = {
    quotePgIdentifier,
    getCurrentTime
};