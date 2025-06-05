def explain_risk_level(risk_code):
    return {
        0: '낮음 - 화재 가능성 거의 없음',
        1: '보통 - 일부 가능성 존재',
        2: '높음 - 주의 필요',
        3: '위험 - 긴급 대응 필요'
    }.get(risk_code, '알 수 없음')
