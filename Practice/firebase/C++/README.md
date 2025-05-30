알고리즘: Firebase_접속_초기화_Cpp
입력: 
  - apiKey
  - projectId
  - appId
  - databaseURL (Realtime DB 사용 시)
  - storageBucket (선택)
출력: 
  - firebase::App* app
  - firebase::auth::Auth* auth
  - firebase::firestore::Firestore* firestore (또는 firebase::database::Database* realtime_db)

1. Firebase C++ SDK 다운로드 및 프로젝트에 연동
   - SDK 압축 해제 후 include/lib 디렉토리를 CMake 또는 빌드 시스템에 등록

2. AppOptions 설정
   AppOptions options;
   options.set_api_key(apiKey);
   options.set_project_id(projectId);
   options.set_app_id(appId);
   options.set_database_url(databaseURL);      // Realtime DB 사용 시
   options.set_storage_bucket(storageBucket);  // Storage 사용 시

3. Firebase 앱 초기화
   App* app = App::Create(options);

4. 서비스 인스턴스 가져오기
   auth ← firebase::auth::Auth::GetAuth(app);
   firestore ← firebase::firestore::Firestore::GetInstance(app);  // Firestore 사용 시
   // realtime_db ← firebase::database::Database::GetInstance(app); // Realtime DB 사용 시

5. (선택) 인증 상태 콜백 등록
   auth->AddAuthStateListener(콜백함수);

6. 애플리케이션 로직 수행
   - 이메일/비밀번호 로그인
   - 문서 읽기/쓰기 (Firestore)
   - 노드 읽기/쓰기 (Realtime DB)

7. 종료 시 리소스 정리
   delete app;