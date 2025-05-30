알고리즘: Firebase_접속_초기화
입력: firebaseConfig (apiKey, authDomain, projectId, storageBucket, messagingSenderId, appId, measurementId 등)
출력: firebaseApp, authService, dbService

1. SDK 모듈(또는 라이브러리) 로드/설치
   - 웹: npm 또는 CDN
   - 안드로이드: Gradle 종속성

2. Firebase 앱 초기화
   firebaseApp ← InitializeApp(firebaseConfig)

3. 인증 서비스 초기화
   authService ← GetAuthService(firebaseApp)

4. 데이터베이스 서비스 초기화
   - Firestore 사용 시: dbService ← GetFirestore(firebaseApp)
   - Realtime DB 사용 시: dbService ← GetDatabase(firebaseApp)

5. (선택) 인증 상태 변경 리스너 등록
   OnAuthStateChanged(authService, callback(user) { … })

6. 반환
   return { firebaseApp, authService, dbService }