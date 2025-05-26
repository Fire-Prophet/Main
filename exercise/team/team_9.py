
module.exports = exportGeoJSON;
"""
}

# 디렉토리 생성 및 파일 저장
os.makedirs(dummy_code_path, exist_ok=True)
for filename, code in dummy_files.items():
    with open(os.path.join(dummy_code_path, filename), "w", encoding="utf-8") as f:
        f.write(code)

# 결과 반환
os.listdir(dummy_code_path)