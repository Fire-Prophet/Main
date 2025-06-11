from googletrans import Translator

translator = Translator()
text = input("번역할 문장을 입력하세요: ")
result = translator.translate(text, src='ko', dest='en')

print("🌍 번역 결과 (영어):", result.text)
