import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.Optional; // Java 8 이상에서 Optional 사용

class Student {
    private String studentId;
    private String name;
    private int age;
    private String major;

    public Student(String studentId, String name, int age, String major) {
        this.studentId = studentId;
        this.name = name;
        this.age = age;
        this.major = major;
    }

    // Getter 메서드
    public String getStudentId() {
        return studentId;
    }

    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }

    public String getMajor() {
        return major;
    }

    // Setter 메서드 (필요에 따라)
    public void setMajor(String major) {
        this.major = major;
    }

    @Override
    public String toString() {
        return String.format("학생 ID: %s, 이름: %s, 나이: %d, 전공: %s",
                             studentId, name, age, major);
    }
}

public class StudentManagement {
    private List<Student> students;
    private Scanner scanner;

    public StudentManagement() {
        students = new ArrayList<>();
        scanner = new Scanner(System.in);
        System.out.println("학생 관리 시스템이 초기화되었습니다.");
    }

    // 학생 추가
    public void addStudent() {
        System.out.println("\n--- 학생 추가 ---");
        System.out.print("학생 ID: ");
        String id = scanner.nextLine();
        
        // ID 중복 체크
        if (findStudentById(id).isPresent()) {
            System.out.println("오류: 이미 존재하는 학생 ID입니다.");
            return;
        }

        System.out.print("이름: ");
        String name = scanner.nextLine();
        System.out.print("나이: ");
        int age = -1;
        try {
            age = Integer.parseInt(scanner.nextLine());
            if (age <= 0) {
                System.out.println("오류: 나이는 양수여야 합니다.");
                return;
            }
        } catch (NumberFormatException e) {
            System.out.println("오류: 유효하지 않은 나이 입력입니다.");
            return;
        }
        System.out.print("전공: ");
        String major = scanner.nextLine();

        Student newStudent = new Student(id, name, age, major);
        students.add(newStudent);
        System.out.println("학생이 성공적으로 추가되었습니다: " + newStudent);
    }

    // 모든 학생 목록 출력
    public void listAllStudents() {
        System.out.println("\n--- 모든 학생 목록 ---");
        if (students.isEmpty()) {
            System.out.println("등록된 학생이 없습니다.");
            return;
        }
        for (Student student : students) {
            System.out.println(student);
        }
        System.out.println("--------------------");
    }

    // 학생 ID로 학생 검색
    public Optional<Student> findStudentById(String studentId) {
        return students.stream()
                       .filter(s -> s.getStudentId().equals(studentId))
                       .findFirst(); // 첫 번째 일치하는 학생을 Optional로 반환
    }

    // 학생 검색 및 정보 출력
    public void searchStudent() {
        System.out.println("\n--- 학생 검색 ---");
        System.out.print("검색할 학생 ID: ");
        String id = scanner.nextLine();

        Optional<Student> foundStudent = findStudentById(id);
        if (foundStudent.isPresent()) {
            System.out.println("학생을 찾았습니다: " + foundStudent.get());
        } else {
            System.out.println("학생 ID '" + id + "'를 가진 학생을 찾을 수 없습니다.");
        }
    }

    // 학생 정보 업데이트 (전공만 변경 가능하도록)
    public void updateStudentMajor() {
        System.out.println("\n--- 학생 전공 업데이트 ---");
        System.out.print("업데이트할 학생 ID: ");
        String id = scanner.nextLine();

        Optional<Student> studentOptional = findStudentById(id);
        if (studentOptional.isPresent()) {
            Student studentToUpdate = studentOptional.get();
            System.out.println("현재 전공: " + studentToUpdate.getMajor());
            System.out.print("새로운 전공 입력: ");
            String newMajor = scanner.nextLine();
            studentToUpdate.setMajor(newMajor);
            System.out.println("학생 " + studentToUpdate.getName() + "의 전공이 성공적으로 업데이트되었습니다.");
            System.out.println("업데이트된 정보: " + studentToUpdate);
        } else {
            System.out.println("학생 ID '" + id + "'를 가진 학생을 찾을 수 없습니다.");
        }
    }

    // 학생 삭제
    public void deleteStudent() {
        System.out.println("\n--- 학생 삭제 ---");
        System.out.print("삭제할 학생 ID: ");
        String id = scanner.nextLine();

        boolean removed = students.removeIf(s -> s.getStudentId().equals(id));
        if (removed) {
            System.out.println("학생 ID '" + id + "'가 성공적으로 삭제되었습니다.");
        } else {
            System.out.println("학생 ID '" + id + "'를 가진 학생을 찾을 수 없습니다.");
        }
    }

    // 메인 메뉴
    public void displayMenu() {
        System.out.println("\n=== 학생 관리 시스템 메뉴 ===");
        System.out.println("1. 학생 추가");
        System.out.println("2. 모든 학생 목록");
        System.out.println("3. 학생 검색 (ID)");
        System.out.println("4. 학생 전공 업데이트");
        System.out.println("5. 학생 삭제");
        System.out.println("0. 종료");
        System.out.print("메뉴를 선택하세요: ");
    }

    public void run() {
        int choice;
        do {
            displayMenu();
            try {
                choice = Integer.parseInt(scanner.nextLine());
                switch (choice) {
                    case 1: addStudent(); break;
                    case 2: listAllStudents(); break;
                    case 3: searchStudent(); break;
                    case 4: updateStudentMajor(); break;
                    case 5: deleteStudent(); break;
                    case 0: System.out.println("시스템을 종료합니다."); break;
                    default: System.out.println("유효하지 않은 선택입니다. 다시 시도하세요.");
                }
            } catch (NumberFormatException e) {
                System.out.println("유효하지 않은 입력입니다. 숫자를 입력하세요.");
                choice = -1; // 루프를 계속하기 위해
            }
        } while (choice != 0);
        scanner.close(); // 스캐너 리소스 해제
    }

    public static void main(String[] args) {
        StudentManagement system = new StudentManagement();
        system.run();
    }
}
