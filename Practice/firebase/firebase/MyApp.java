import com.google.firebase.FirebaseApp;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.database.FirebaseDatabase;

public class MyApp extends Application {
  @Override
  public void onCreate() {
    super.onCreate();
    // 앱 초기화
    FirebaseApp.initializeApp(this);
  }
}