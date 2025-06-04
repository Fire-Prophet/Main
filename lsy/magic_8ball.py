import random

input("질문을 입력하세요: ")
responses = [
    "그럼요!", "아마도요.", "지켜봐야죠.", "글쎄요...", "절대 안돼요!", "확신할 수 없어요."
]
print("마법의 8볼:", random.choice(responses))
