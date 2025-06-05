import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.ArrayList;

public class FileProcessor {

    private static final String INPUT_FILE_NAME = "input.txt";
    private static final String OUTPUT_FILE_NAME = "output.txt";

    public static void main(String[] args) {
        // 샘플 입력 파일 생성
        createSampleInputFile();

        // 파일 읽기 및 처리
        List<String> processedLines = new ArrayList<>();
        System.out.println("--- 파일 읽기 및 처리 시작 ---");
        try (BufferedReader reader = new BufferedReader(new FileReader(INPUT_FILE_NAME))) {
            String line;
            int lineNumber = 1;
            while ((line = reader.readLine()) != null) {
                System.out.println(String.format("읽은 줄 %d: %s", lineNumber, line));
                processedLines.add(line.toUpperCase()); // 읽은 내용을 대문자로 변환하여 저장
                lineNumber++;
            }
            System.out.println("파일 읽기 완료.");
        } catch (IOException e) {
            System.err.println("파일 읽기 중 오류 발생: " + e.getMessage());
        }

        // 처리된 내용 파일에 쓰기
        System.out.println("\n--- 처리된 내용 파일에 쓰기 시작 ---");
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(OUTPUT_FILE_NAME))) {
            for (String processedLine : processedLines) {
                writer.write(processedLine);
                writer.newLine(); // 각 줄마다 새 줄 추가
            }
            System.out.println("처리된 내용을 파일에 성공적으로 작성했습니다: " + OUTPUT_FILE_NAME);
        } catch (IOException e) {
            System.err.println("파일 쓰기 중 오류 발생: " + e.getMessage());
        }

        // 생성된 파일들 정리 (선택 사항)
        cleanUpFiles();
        System.out.println("\n--- 프로그램 종료 ---");
    }

    private static void createSampleInputFile() {
        String content = "Hello, Java File I/O!\nThis is the second line.\nLast line for demonstration.";
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(INPUT_FILE_NAME))) {
            writer.write(content);
            System.out.println("샘플 입력 파일 생성 완료: " + INPUT_FILE_NAME);
        } catch (IOException e) {
            System.err.println("샘플 입력 파일 생성 중 오류: " + e.getMessage());
        }
    }

    private static void cleanUpFiles() {
        Path inputPath = Paths.get(INPUT_FILE_NAME);
        Path outputPath = Paths.get(OUTPUT_FILE_NAME);
        try {
            if (Files.exists(inputPath)) {
                Files.delete(inputPath);
                System.out.println(INPUT_FILE_NAME + " 삭제 완료.");
            }
            if (Files.exists(outputPath)) {
                Files.delete(outputPath);
                System.out.println(OUTPUT_FILE_NAME + " 삭제 완료.");
            }
        } catch (IOException e) {
            System.err.println("파일 정리 중 오류 발생: " + e.getMessage());
        }
    }
}
