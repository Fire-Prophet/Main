exports.track = async (label, fn) => {
  const start = Date.now();
  const result = await fn();
  const duration = Date.now() - start;
  console.log(`[${label}] 처리 시간: ${duration}ms`);
  return result;
};
