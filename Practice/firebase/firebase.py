import firebase_admin
from firebase_admin import credentials, auth, firestore, db

# 1) 서비스 계정 키로 앱 초기화
cred = credentials.Certificate("serviceAccountKey.json")
# Firestore만 쓸 때:
app = firebase_admin.initialize_app(cred)
# Realtime DB를 쓰려면 URL 지정:
# app = firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://<YOUR_PROJECT_ID>.firebaseio.com'
# })

# 2) 인증(Auth) 서비스
# (사용자 생성, UID로 조회 등 관리 기능)
user = auth.get_user_by_email("user@example.com")
print("User UID:", user.uid)

# 3) Firestore 사용 예 (문서 읽기/쓰기)
fs = firestore.client(app)
# 쓰기
doc_ref = fs.collection("todos").document()
doc_ref.set({
    "text": "파이어스토어 테스트",
    "createdAt": firestore.SERVER_TIMESTAMP
})
print("새 문서 ID:", doc_ref.id)
# 읽기
for doc in fs.collection("todos").stream():
    print(doc.id, doc.to_dict())

# 4) Realtime DB 사용 예 (노드 읽기/쓰기)
# rt = db.reference('/', app=app)
# rt.child('messages').push({
#     'text': 'Realtime DB 테스트'
# })
# print(rt.child('messages').get())