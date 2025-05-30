import com.google.firebase.FirebaseApp;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.database.FirebaseDatabase;

// 3. 인증 및 DB 사용
public class MainActivity extends AppCompatActivity {
  private FirebaseAuth auth;
  private FirebaseFirestore firestore;
  private FirebaseDatabase realtimeDb;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    // 서비스 인스턴스 가져오기
    auth = FirebaseAuth.getInstance();
    firestore = FirebaseFirestore.getInstance();
    realtimeDb = FirebaseDatabase.getInstance();

    // 인증 상태 리스너
    auth.addAuthStateListener(firebaseAuth -> {
      FirebaseUser user = firebaseAuth.getCurrentUser();
      if (user != null) {
        Log.d("Auth", "로그인 됨: " + user.getUid());
      } else {
        Log.d("Auth", "로그아웃 됨");
      }
    });
  }

  // 이메일/비밀번호 로그인
  public void signIn(String email, String pw) {
    auth.signInWithEmailAndPassword(email, pw)
      .addOnCompleteListener(this, task -> {
        if (task.isSuccessful()) {
          Log.d("Auth", "로그인 성공");
        } else {
          Log.e("Auth", "로그인 실패", task.getException());
        }
      });
  }

  // Firestore 읽기/쓰기
  private void writeFirestore() {
    Map<String, Object> data = new HashMap<>();
    data.put("msg", "Hello, Firebase!");
    firestore.collection("messages")
             .add(data)
             .addOnSuccessListener(docRef ->
               Log.d("Firestore", "문서 ID: " + docRef.getId()))
             .addOnFailureListener(e ->
               Log.e("Firestore", "쓰기 오류", e));
  }
}