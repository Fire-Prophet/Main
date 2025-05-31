use std::env; // 환경 변수(명령줄 인수)를 위한 모듈
use std::fs;  // 파일 시스템 작업을 위한 모듈
use std::io::{self, Read}; // I/O 관련 트레이트 및 함수

fn main() {
    // 명령줄 인수 수집
    // env::args()는 프로그램 이름 포함하여 Iterator를 반환합니다.
    let args: Vec<String> = env::args().collect();

    // 인수가 올바르게 제공되었는지 확인
    if args.len() < 2 {
        eprintln!("사용법: {} <파일_경로>", args[0]);
        eprintln!("파일에서 내용을 읽어 터미널에 출력합니다.");
        // 오류 메시지 출력 후 프로그램 종료
        std::process::exit(1); 
    }

    // 두 번째 인수는 파일 경로여야 합니다.
    let file_path = &args[1]; 

    println!("'{}' 파일을 읽으려 합니다...", file_path);

    // 파일에서 내용 읽기
    // fs::read_to_string 함수는 파일 내용을 String으로 읽어옵니다.
    // Result<String, io::Error>를 반환하므로, unwrap_or_else로 오류 처리합니다.
    let contents = fs::read_to_string(file_path)
        .unwrap_or_else(|err| {
            // 파일을 읽는 데 실패하면 오류 메시지 출력 후 종료
            eprintln!("오류: '{}' 파일을 읽을 수 없습니다: {}", file_path, err);
            std::process::exit(1);
        });

    println!("\n--- 파일 내용 ---");
    println!("{}", contents);
    println!("-----------------\n");

    // 추가: 파일 크기 정보 얻기 (메타데이터 활용)
    match fs::metadata(file_path) {
        Ok(metadata) => {
            println!("파일 크기: {} 바이트", metadata.len());
            println!("수정 시간: {:?}", metadata.modified().ok()); // Optional<SystemTime> 반환
        },
        Err(err) => {
            eprintln!("오류: 파일 메타데이터를 가져올 수 없습니다: {}", err);
        }
    }

    println!("성공적으로 파일을 읽었습니다.");
}

// 이 파일을 컴파일하고 실행하는 방법:
// 1. `touch example.txt` 또는 `echo "Hello Rust!\nThis is a test file." > example.txt` 로 파일 생성
// 2. `rustc cli_file_reader.rs`
// 3. `./cli_file_reader example.txt`
// 4. (오류 테스트) `./cli_file_reader non_existent_file.txt` 또는 `./cli_file_reader`
