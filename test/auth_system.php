<?php
// 세션 시작
session_start();

// 데이터베이스 대신 간단한 사용자 배열 (실제 앱에서는 DB 사용)
$users = [
    'user1' => ['password' => 'pass123', 'role' => 'admin'],
    'user2' => ['password' => 'abc456', 'role' => 'user'],
];

// 로그인 함수
function login($username, $password) {
    global $users; // 전역 변수 users에 접근

    if (isset($users[$username]) && $users[$username]['password'] === $password) {
        $_SESSION['logged_in'] = true;
        $_SESSION['username'] = $username;
        $_SESSION['role'] = $users[$username]['role'];
        echo "<p style='color: green;'>로그인 성공! 환영합니다, {$username}님.</p>";
        return true;
    } else {
        echo "<p style='color: red;'>로그인 실패: 잘못된 사용자 이름 또는 비밀번호입니다.</p>";
        return false;
    }
}

// 로그아웃 함수
function logout() {
    session_unset();   // 모든 세션 변수 제거
    session_destroy(); // 세션 파괴
    echo "<p style='color: blue;'>로그아웃되었습니다.</p>";
    header("Refresh: 2; url=auth_system.php"); // 2초 후 페이지 새로고침
    exit();
}

// 로그인 상태 확인
function is_logged_in() {
    return isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true;
}

// 역할 확인 (예: 관리자만 접근 가능)
function is_admin() {
    return is_logged_in() && $_SESSION['role'] === 'admin';
}

// 폼 제출 처리
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action']) && $_POST['action'] === 'login') {
        $username = $_POST['username'] ?? '';
        $password = $_POST['password'] ?? '';
        login($username, $password);
    } elseif (isset($_POST['action']) && $_POST['action'] === 'logout') {
        logout();
    }
}
?>

<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP 간단한 인증 시스템</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
        .container { background-color: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 400px; margin: 30px auto; }
        input[type="text"], input[type="password"] { width: calc(100% - 22px); padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
        input[type="submit"], button { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 10px; }
        input[type="submit"]:hover, button:hover { background-color: #0056b3; }
        p { margin-top: 15px; }
        .admin-section { border: 1px dashed #ccc; padding: 15px; margin-top: 20px; background-color: #ffe; }
    </style>
</head>
<body>

    <div class="container">
        <h2>PHP 인증 시스템</h2>

        <?php if (is_logged_in()): ?>
            <p>현재 로그인된 사용자: <strong><?php echo htmlspecialchars($_SESSION['username']); ?></strong> (역할: <?php echo htmlspecialchars($_SESSION['role']); ?>)</p>
            <form method="POST">
                <input type="hidden" name="action" value="logout">
                <input type="submit" value="로그아웃">
            </form>

            <?php if (is_admin()): ?>
                <div class="admin-section">
                    <h3>관리자 전용 페이지</h3>
                    <p>이 내용은 관리자(user1)만 볼 수 있습니다.</p>
                    <ul>
                        <li>사용자 관리</li>
                        <li>시스템 설정</li>
                        <li>로그 확인</li>
                    </ul>
                </div>
            <?php else: ?>
                <p>일반 사용자 페이지입니다. 관리자 전용 콘텐츠는 볼 수 없습니다.</p>
            <?php endif; ?>

        <?php else: ?>
            <h3>로그인</h3>
            <form method="POST">
                <input type="hidden" name="action" value="login">
                <label for="username">사용자 이름:</label><br>
                <input type="text" id="username" name="username" required><br>
                <label for="password">비밀번호:</label><br>
                <input type="password" id="password" name="password" required><br>
                <input type="submit" value="로그인">
            </form>
            <p>테스트 계정:</p>
            <ul>
                <li>사용자: user1 / 비밀번호: pass123 (관리자)</li>
                <li>사용자: user2 / 비밀번호: abc456 (일반 사용자)</li>
            </ul>
        <?php endif; ?>
    </div>

</body>
</html>
