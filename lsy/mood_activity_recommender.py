mood = input("오늘 기분은 어떤가요? (예: 슬픔, 기쁨, 화남): ").strip()

activities = {
    "기쁨": ["산책하기", "친구와 대화하기", "좋아하는 음악 듣기"],
    "슬픔": ["따뜻한 차 마시기", "조용한 산책", "감성 영화 보기"],
    "화남": ["스트레칭", "운동하기", "일기 쓰기"]
}

recommend = activities.get(mood)

if recommend:
    print("💡 오늘 기분에 어울리는 활동:")
    for act in recommend:
        print(f"- {act}")
else:
    print("😶 해당 기분에 맞는 활동을 찾을 수 없어요.")
