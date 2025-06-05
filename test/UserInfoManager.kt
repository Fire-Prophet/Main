import java.time.LocalDate
import java.time.format.DateTimeParseException
import java.util.Scanner

// 사용자 정보를 저장하는 데이터 클래스 (불변 객체)
data class User(
    val id: String,
    val name: String,
    val email: String,
    val dateOfBirth: LocalDate // Java 8의 LocalDate 사용
) {
    // computed property: 나이 계산
    val age: Int
        get() = LocalDate.now().year - dateOfBirth.year

    // 사용자 정보 출력 메서드
    fun displayInfo() {
        println("--- 사용자 정보 ---")
        println("ID: $id")
        println("이름: $name")
        println("이메일: $email")
        println("생년월일: $dateOfBirth (만 ${age}세)")
        println("------------------")
    }
}

class UserManager {
    private val users = mutableListOf<User>() // 사용자 목록을 저장할 리스트
    private val scanner = Scanner(System.in)

    init {
        println("사용자 관리 시스템이 초기화되었습니다.")
    }

    // 새 사용자 추가
    fun addUser() {
        println("\n--- 새 사용자 추가 ---")
        print("사용자 ID: ")
        val id = scanner.nextLine().trim()
        if (id.isBlank()) {
            println("오류: 사용자 ID는 비워둘 수 없습니다.")
            return
        }
        if (users.any { it.id == id }) { // ID 중복 체크
            println("오류: 이미 존재하는 사용자 ID입니다.")
            return
        }

        print("이름: ")
        val name = scanner.nextLine().trim()
        if (name.isBlank()) {
            println("오류: 이름은 비워둘 수 없습니다.")
            return
        }

        print("이메일: ")
        val email = scanner.nextLine().trim()
        if (!email.contains("@") || !email.contains(".")) { // 간단한 이메일 유효성 검사
            println("오류: 유효하지 않은 이메일 형식입니다.")
            return
        }

        print("생년월일 (YYYY-MM-DD): ")
        val dobString = scanner.nextLine().trim()
        val dateOfBirth: LocalDate
        try {
            dateOfBirth = LocalDate.parse(dobString)
        } catch (e: DateTimeParseException) {
            println("오류: 유효하지 않은 생년월일 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")
            return
        }
        
        val newUser = User(id, name, email, dateOfBirth)
        users.add(newUser)
        println("사용자 '${name}'이(가) 성공적으로 추가되었습니다.")
    }

    // 모든 사용자 목록 출력
    fun listAllUsers() {
        println("\n--- 모든 사용자 목록 ---")
        if (users.isEmpty()) {
            println("등록된 사용자가 없습니다.")
            return
        }
        users.forEach { it.displayInfo() }
        println("------------------------")
    }

    // ID로 사용자 검색
    fun findUserById() {
        println("\n--- 사용자 검색 (ID) ---")
        print("검색할 사용자 ID: ")
        val id = scanner.nextLine().trim()
        
        val foundUser = users.find { it.id == id } // find 확장 함수 사용
        if (foundUser != null) {
            println("사용자를 찾았습니다:")
            foundUser.displayInfo()
        } else {
            println("사용자 ID '$id'를 가진 사용자를 찾을 수 없습니다.")
        }
    }

    // 사용자 삭제
    fun deleteUser() {
        println("\n--- 사용자 삭제 ---")
        print("삭제할 사용자 ID: ")
        val id = scanner.nextLine().trim()

        val initialSize = users.size
        users.removeIf { it.id == id } // removeIf 함수 사용
        if (users.size < initialSize) {
            println("사용자 ID '$id'가 성공적으로 삭제되었습니다.")
        } else {
            println("사용자 ID '$id'를 가진 사용자를 찾을 수 없습니다.")
        }
    }

    // 메인 메뉴 표시
    fun displayMenu() {
        println("\n=== 사용자 관리 시스템 메뉴 ===")
        println("1. 사용자 추가")
        println("2. 모든 사용자 목록")
        println("3. 사용자 검색 (ID)")
        println("4. 사용자 삭제")
        println("0. 종료")
        print("메뉴를 선택하세요: ")
    }

    // 시스템 실행
    fun run() {
        var choice: Int
        do {
            displayMenu()
            choice = try {
                scanner.nextLine().toInt()
            } catch (e: NumberFormatException) {
                -1 // 유효하지 않은 입력
            }

            when (choice) {
                1 -> addUser()
                2 -> listAllUsers()
                3 -> findUserById()
                4 -> deleteUser()
                0 -> println("시스템을 종료합니다.")
                else -> println("유효하지 않은 선택입니다. 다시 시도하세요.")
            }
        } while (choice != 0)
        scanner.close()
    }
}

fun main() {
    val userManager = UserManager()
    userManager.run()
}
