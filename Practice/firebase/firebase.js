// 1. SDK 설치 (터미널)
// npm install firebase

// 2. 모듈 가져오기
import { initializeApp } from "firebase/app";
import { getAuth, onAuthStateChanged, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore } from "firebase/firestore";           // Firestore
// import { getDatabase } from "firebase/database";           // Realtime DB 사용 시

// 3. 프로젝트 설정 정보
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "SENDER_ID",
  appId: "APP_ID",
  measurementId: "MEASUREMENT_ID"
};

// 4. 앱 초기화
const app = initializeApp(firebaseConfig);

// 5. 서비스 초기화
const auth = getAuth(app);
const db = getFirestore(app);             // Firestore
// const db = getDatabase(app);           // Realtime DB

// 6. 인증 상태 리스너
onAuthStateChanged(auth, user => {
  if (user) {
    console.log("로그인 됨:", user.uid);
  } else {
    console.log("로그아웃 됨");
  }
});

// 7. 이메일/비밀번호 로그인 예시
async function login(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    console.log("로그인 성공:", userCredential.user.uid);
  } catch (error) {
    console.error("로그인 오류:", error.code, error.message);
  }
}

// 8. 데이터 읽기/쓰기 예시 (Firestore)
import { collection, getDocs, addDoc } from "firebase/firestore";

async function fetchTodos() {
  const snapshot = await getDocs(collection(db, "todos"));
  snapshot.forEach(doc => {
    console.log(doc.id, "=>", doc.data());
  });
}

async function addTodo(item) {
  const ref = await addDoc(collection(db, "todos"), { text: item, createdAt: Date.now() });
  console.log("새 문서 ID:", ref.id);
}