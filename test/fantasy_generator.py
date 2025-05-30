import random

# 사용자 설정 기반 데이터
races = ["엘프", "드워프", "인간", "오크", "하플링", "잊혀진 자", "고대 정령"]
classes = ["기사", "마법사", "도적", "성직자", "음유시인", "방랑자", "수호자"]
adjectives = ["고독한", "기억을 잃은", "전설적인", "저주받은", "희망을 찾는", "마지막"]
locations = ["잊혀진 왕국", "세계의 끝자락", "고대 도서관", "속삭이는 숲", "시간의 균열"]
goals = ["잃어버린 기억을 찾기 위해", "고대 유물을 수호하기 위해", "옛 동료를 찾기 위해", 
         "세상의 종언을 막은 대가를 알기 위해", "자신의 '이야기' 조각을 맞추기 위해", "평온한 안식처를 찾기 위해"]
obstacles = ["그를 알아보지 못하는 세상", "기억을 노리는 그림자", "고대의 저주", 
             "과거의 환영", "강력한 라이벌", "자신의 존재에 대한 회의감", "시간의 흐름 자체"]

def generate_character_profile():
    """간단한 판타지 캐릭터 프로필을 생성합니다."""
    adj = random.choice(adjectives)
    race = random.choice(races)
    klass = random.choice(classes)
    
    # 주인공 설정 강조
    if random.random() < 0.2: # 20% 확률로 주인공 컨셉 적용
        return f"캐릭터: 기억을 잃은 불멸의 기사, {adj} {race}의 모습으로 {random.choice(locations)}에서 발견되다."
    else:
        return f"캐릭터: {adj} {race} {klass}"

def generate_plot_hook():
    """간단한 플롯 아이디어를 생성합니다."""
    character = generate_character_profile()
    goal = random.choice(goals)
    obstacle = random.choice(obstacles)
    location = random.choice(locations)
    
    return f"플롯: {character}(은)는 {location}에서 {goal}, 하지만 {obstacle}(이)라는 예기치 못한 난관에 부딪힌다."

def generate_legend_snippet():
    """주인공에 대한 잊혀진 전설 조각을 생성합니다."""
    actions = ["홀로 군단을 막아섰던", "세계의 심장을 지켰던", "별빛으로 검을 벼렸던"]
    results = ["이제는 이름조차 희미해진", "오직 바람만이 그를 노래하는", "아이들의 옛이야기에만 남은"]
    return f"전설: {random.choice(actions)} 그 영웅... {random.choice(results)} 이름 없는 기사에 대한 이야기."


print("--- 판타지 아이디어 생성기 ---")
print("\n[캐릭터 프로필]")
print(generate_character_profile())

print("\n[플롯 훅]")
print(generate_plot_hook())

print("\n[잊혀진 전설 조각]")
print(generate_legend_snippet())

print("\n--- 당신의 주인공을 위한 영감 ---")
print(f"* 불멸의 기사는 {random.choice(locations)}에서 자신의 {random.choice(['잃어버린 검', '깨진 방패', '바랜 망토'])} 조각을 발견하고, 희미한 기억의 실마리를 쫓기 시작한다.")
