import random

music_dict = {
    '슬픔': {
        'Korean': [
            "백예린 - 그건 아마 우리의 잘못은 아닐 거야",
            "악뮤 - 오랜 날 오랜 밤",
            "아이유 - 마음"
        ],
        'Japanese': [
            "Aimer - Ref:rain",
            "YOASOBI - たぶん",
            "米津玄師 - Lemon"
        ],
        'English': [
            "Adele - Someone Like You",
            "Billie Eilish - when the party's over",
            "Lewis Capaldi - Someone You Loved"
        ]
    },
    '신남': {
        'Korean': [
            "세븐틴 - 아주 NICE",
            "싸이 - DADDY",
            "IVE - I AM"
        ],
        'Japanese': [
            "YOASOBI - 怪物",
            "Aimer - STAND-ALONE",
            "LiSA - 紅蓮華"
        ],
        'English': [
            "Dua Lipa - Levitating",
            "Katy Perry - Roar",
            "Bruno Mars - Uptown Funk"
        ]
    },
    '우울': {
        'Korean': [
            "10cm - 폰서트",
            "자우림 - 샤이닝",
            "윤하 - 사건의 지평선"
        ],
        'Japanese': [
            "Eve - 心予報",
            "Aimer - カタオモイ",
            "米津玄師 - 灰色と青"
        ],
        'English': [
            "Coldplay - Fix You",
            "Radiohead - Creep",
            "Nirvana - Something In The Way"
        ]
    },
    '평온': {
        'Korean': [
            "검정치마 - 기다린 만큼, 더",
            "정승환 - 눈사람",
            "적재 - 나랑 같이 걸을래"
        ],
        'Japanese': [
            "King Gnu - 白日",
            "藤井風 - きらり",
            "宇多田ヒカル - First Love"
        ],
        'English': [
            "Norah Jones - Don't Know Why",
            "Daniel Caesar - Best Part",
            "Lauv - Paris in the Rain"
        ]
    }
}

mood = input("지금 기분은? (슬픔, 신남, 우울, 평온): ")
language = input("듣고 싶은 언어는? (Korean, Japanese, English): ")

if mood in music_dict and language in music_dict[mood]:
    song = random.choice(music_dict[mood][language])
    print(f"🎵 추천곡 ({mood}, {language}): {song}")
else:
    print("올바른 기분이나 언어를 입력해주세요.")
