#include <iostream>
#include <thread>
#include <chrono>

#include <firebase/app.h>
#include <firebase/auth.h>
#include <firebase/firestore.h>
// #include <firebase/database.h>  // Realtime DB 사용 시

using namespace firebase;
using namespace firebase::auth;
using namespace firebase::firestore;

int main() {
  // 1) AppOptions 구성
  AppOptions options;
  options.set_api_key("YOUR_API_KEY");
  options.set_project_id("YOUR_PROJECT_ID");
  options.set_app_id("YOUR_APP_ID");
  options.set_database_url("https://YOUR_PROJECT_ID.firebaseio.com");  // Realtime DB
  options.set_storage_bucket("YOUR_PROJECT_ID.appspot.com");           // Storage

  // 2) Firebase 앱 초기화
  App* app = App::Create(options);

  // 3) 서비스 인스턴스 가져오기
  Auth* auth = Auth::GetAuth(app);
  Firestore* db = Firestore::GetInstance(app);
  // Database* rt_db = database::Database::GetInstance(app);  // Realtime DB

  // 4) 이메일/비밀번호 로그인
  std::cout << "로그인 시도 중..." << std::endl;
  auth->SignInWithEmailAndPassword("user@example.com", "password")
    .OnCompletion([&](const Future<AuthResult>& result) {
      if (result.error() == 0) {
        std::cout << "로그인 성공! UID = "
                  << result.result()->user.uid() << std::endl;
      } else {
        std::cerr << "로그인 실패: " << result.error_message() << std::endl;
      }
    });

  // 비동기 작업이 완료될 때까지 약간 대기
  std::this_thread::sleep_for(std::chrono::seconds(2));

  // 5) Firestore에 문서 쓰기
  MapFieldValue data;
  data["text"] = FieldValue::String("C++ Firestore 테스트");
  std::cout << "문서 쓰기 중..." << std::endl;
  db->Collection("todos").Add(data)
    .OnCompletion([&](const Future<DocumentReference>& result) {
      if (result.error() == 0) {
        std::cout << "새 문서 ID: "
                  << result.result()->id() << std::endl;
      } else {
        std::cerr << "쓰기 실패: " << result.error_message() << std::endl;
      }
    });

  std::this_thread::sleep_for(std::chrono::seconds(2));

  // 6) Firestore에서 문서 읽기
  std::cout << "문서 조회 중..." << std::endl;
  db->Collection("todos").Get()
    .OnCompletion([&](const Future<QuerySnapshot>& result) {
      if (result.error() == 0) {
        for (const DocumentSnapshot& doc : *result.result()) {
          std::cout << doc.id() << " => ";
          auto fields = doc.GetData();
          for (auto& kv : fields) {
            std::cout << kv.first << ": ";
            if (kv.second.is_string()) {
              std::cout << kv.second.string_value();
            }
            std::cout << "; ";
          }
          std::cout << std::endl;
        }
      } else {
        std::cerr << "조회 실패: " << result.error_message() << std::endl;
      }
    });

  std::this_thread::sleep_for(std::chrono::seconds(2));

  // 7) 앱 종료
  delete app;
  return 0;
}