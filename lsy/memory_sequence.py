import random

class Sequence:
    def __init__(self, length, category):
        self.length = length
        self.category = category
        self.sequence = self.generate()

    def generate(self):
        if self.category == "1":  # 숫자
            return [random.randint(0, 9) for _ in range(self.length)]
        elif self.category == "2":  # 한글 단어
            words = ["사과", "학교", "바다", "하늘", "고양이", "강아지", "나무", "의자", "컴퓨터", "음악",
                     "책상", "핸드폰", "창문", "달력", "커피", "바람", "강", "비", "눈", "소리",
                     "버스", "기차", "도로", "산책", "꽃", "별", "노래", "식물", "라디오", "편지"]
        elif self.category == "3":  # 색상
            words = ["빨강", "주황", "노랑", "초록", "파랑", "남색", "보라", "분홍", "갈색", "회색",
                     "하양", "검정", "연두", "청록", "자주", "살구", "하늘색", "연분홍", "카키", "은색",
                     "금색", "청색", "버건디", "인디고", "와인", "연보라", "크림색", "밤색", "청바지색", "아이보리"]
        else:  # 영어 단어
            words = ["apple", "school", "sea", "sky", "cat", "dog", "tree", "chair", "computer", "music",
                     "desk", "phone", "window", "calendar", "coffee", "wind", "river", "rain", "snow", "sound",
                     "bus", "train", "road", "walk", "flower", "star", "song", "plant", "radio", "letter"]
        return random.choices(words, k=self.length)

    def show(self):
        print("\n🔢 기억하세요!")
        print(" ".join(str(item) for item in self.sequence))

    def check(self, user_input):
        if self.category == "1":
            # 숫자는 붙여서 입력해도 정답 인정
            return list(user_input.strip()) == [str(n) for n in self.sequence]
        else:
            input_list = [item.strip() for item in user_input.replace(",", " ").split()]
            return input_list == [str(item) for item in self.sequence]
