module.exports = function validateInput(data) {
  const { temp, humidity, wind } = data;
  if (
    typeof temp !== 'number' || typeof humidity !== 'number' || typeof wind !== 'number'
  ) {
    throw new Error('입력값은 모두 숫자여야 합니다.');
  }
};
