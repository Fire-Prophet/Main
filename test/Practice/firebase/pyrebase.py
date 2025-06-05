import pyrebase
import json

# Firebase 설정
with open('firebase_config.json') as f:
    firebase_config = json.load(f)

# 1) 초기화
firebase = pyrebase.initialize_app(firebase_config)

# 2) 인증(Auth)
auth = firebase.auth()
# 이메일/비밀번호 로그인
email = "user@example.com"
password = "yourpassword"
user = auth.sign_in_with_email_and_password(email, password)
print("로그인 성공, 토큰:", user['idToken'])

# 3) Realtime DB 읽기/쓰기
db = firebase.database()
# 쓰기
data = {"text": "파이리얼타임DB 테스트"}
db.child("messages").push(data, user['idToken'])
# 읽기
messages = db.child("messages").get(user['idToken'])
for msg in messages.each():
    print(msg.key(), msg.val())

# 4) Storage 예시 (파일 업로드)
storage = firebase.storage()
local_path = "local_image.png"
remote_path = "images/remote_image.png"
storage.child(remote_path).put(local_path, user['idToken'])
print("다운로드 URL:", storage.child(remote_path).get_url(user['idToken']))